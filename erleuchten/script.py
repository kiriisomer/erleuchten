# coding:utf-8

# test_script_class


# import time
import signal
import os
import subprocess
import shutil

from erleuchten.util import conf
from erleuchten.util import error
from erleuchten.util.xml import ScriptConf


SHELL_EXECUTOR = '/bin/sh'


SCRIPT_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_STATUS_RUNNING = 'RUNNING'   # 运行状态

SCRIPT_SET_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_SET_STATUS_NEW = 'NEW'           # 新对象，没有配置文件
SCRIPT_SET_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_SET_STATUS_RUNNING = 'RUNNING'   # 运行状态


class CommandTimeoutError(Exception):
    pass


def create(name, script_name):
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_name != "":
        # 已经存在了
        print("name already existed")
        return

    script_obj.initial(name, script_name)


def remove(name):
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_name != "":
        # 存在,可以删掉
        del script_obj
        shutil.rmtree(os.path.join(conf.PATH_SCRIPT, name))


def run(name):
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_name == "":
        print("script not found")
        return

    if script_obj.status == SCRIPT_STATUS_STOP:
        script_obj.run()
    else:
        print("script status is not STOP")


def timeout_handler(signum, frame):
    """SIGALRM注册函数"""
    raise CommandTimeoutError


class Script(object):
    """single test script"""

    def __init__(self):
        self.name = ""
        self.script_name = ""
        self.pid = -1
        self.exceed_time = 0    # 超时时间
        self.status = SCRIPT_STATUS_UNKNOWN
        self.stdout = None

    def initial(self, name, script_name, exceed_time=0, stdout=None):
        """初始化一个新的对象"""
        self.name = name
        self.set_script(script_name)
        self.status = SCRIPT_STATUS_STOP
        self.exceed_time = exceed_time
        self.stdout = stdout

    def set_stdout(self, stdout):
        self.stdout = stdout

    def set_script(self, script_name):
        """将脚本复制进来"""
        self.script_name = script_name
        filename = os.path.split(script_name)[1]
        new_path = os.path.join(conf.PATH_SCRIPT, self.name, filename)
        shutil.copy(script_name, new_path)
        self.script_name = new_path

    def run(self, stdout=None):
        """run script
        根据不同的情况会返回不同类型的值(None，数字，字符串)"""
        if stdout is not None:
            self.stdout = stdout
        signal.signal(signal.SIGALRM, timeout_handler)
        batch = os.path.join(conf.PATH_SCRIPT, self.name, self.script_name)
        cmd_list = [SHELL_EXECUTOR, batch]
        try:
            signal.alarm(self.exceed_time)
            p = subprocess.Popen(cmd_list, stdout=self.stdout)
            self.pid = p.pid
            p.wait()
            exit_code = p.returncode
            signal.alarm(0)
            return exit_code
        except CommandTimeoutError:
            p.kill()
            return "TimeExceed"

    def check_exist(self):
        """"""

    def load_conf(self):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        conf_obj = ScriptConf(os.path.join(conf.PATH_SCRIPT, self.name,
                                           "%s.conf" % self.name), self.name)
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj.xml_root_obj is None and conf_obj.get_name() is None:
            return
            # raise error.ScriptError(error.ERRNO_SCRIPT_OPENCONF_ERROR)
        conf_dict = conf_obj.load_config()
        self.script_name = conf_dict["script_name"]
        self.pid = conf_dict["pid"]
        self.exceed_time = conf_dict["exceed_time"]
        self.status = conf_dict["status"]

    def save_conf(self):
        """保存配置到文件"""
        conf_dict = {
            "name": self.name,
            "script_name": self.script_name,
            "pid": self.pid,
            "exceed_time": self.exceed_time,
            "status": self.status,
        }
        self.conf_obj.save_config(conf_dict)

    def interrupt(self):
        """force stop script"""
        pass
        if self.pid > 0:
            os.kill(self.pid, signal.SIGKILL)


class ScriptSet(object):
    """a series of test script set"""

    def __init__(self):
        self.name = ""
        self.script_list = []
        self.stdout = None
        self.stderr = None
        self.exit_code_list = []

    def initial(self, name):
        """"""
        self.name = name
        self.load_conf()

    def load_conf(self):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        conf_obj = ScriptConf(os.path.join(conf.PATH_SCRIPT_SET, self.name,
                                           "%s.conf" % self.name), self.name)
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj is None and conf_obj.get_name() is None:
            raise error.ScriptError(error.ERRNO_SCRIPT_OPENCONF_ERROR)
        conf_dict = conf_obj.load_config()
        self.script_list = conf_dict["script_list"]
        self.stdout = conf_dict["stdout"]
        self.stderr = conf_dict["stderr"]
        self.exit_code_list = conf_dict["exit_code_list"]

    def set_testscript(self, script_list):
        """设置测试脚本"""
        self.script_list = script_list

    def run(self):
        """run scripts"""
        exit_code_list = []
        for ts in self.script_list:
            if isinstance(ts, Script):
                try:
                    exit_code = ts.run()
                    exit_code_list.append(exit_code)
                except:
                    exit_code_list.append("UnexpectedException")
            else:
                exit_code_list.append("CommandFormatError")
        self.exit_code_list = exit_code_list
        return exit_code_list

    def get_result(self):
        return self.exit_code_list
