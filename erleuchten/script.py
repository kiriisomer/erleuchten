# coding:utf-8

# test_script_class


# import time
import signal
import os
import subprocess
import shutil

from erleuchten.util import conf
from erleuchten.util import error
from erleuchten.util.xml import ScriptConf, ScriptSetConf


SHELL_EXECUTOR = '/bin/sh'


SCRIPT_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_STATUS_RUNNING = 'RUNNING'   # 运行状态

SCRIPT_SET_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_SET_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_SET_STATUS_RUNNING = 'RUNNING'   # 运行状态


class CommandTimeoutError(Exception):
    pass


# ==============================================================================
#
# ==============================================================================
def create_script(name, script_name):
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_name != "":
        # 已经存在了
        print("name already existed")
        return

    script_obj.initial(name, script_name)


def remove_script(name):
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_name != "":
        # 存在,可以删掉
        del script_obj
        shutil.rmtree(os.path.join(conf.PATH_SCRIPT, name))


def run_script(name):
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_name == "":
        print("script not found")
        return

    if script_obj.status == SCRIPT_STATUS_STOP:
        script_obj.run()
    else:
        print("script status is not STOP")


# ==============================================================================
#
# ==============================================================================
def create_script_set(name, script_names):
    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)
    if script_set_obj.script_name != "":
        # 已经存在了
        print("name already existed")
        return

    script_set_obj.initial(name, script_names)


def set_script_set(name, script_names):
    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)
    if script_set_obj.script_name == "":
        # 不存在
        print("script set not found")
        return

    script_set_obj.initial(name, script_names)


def remove_script_set(name, force=False):
    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)
    if script_set_obj.script_name != "":
        # 存在,可以删掉
        del script_set_obj
        shutil.rmtree(os.path.join(conf.PATH_SCRIPT_SET, name))


def run_script_set(name):
    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)
    if script_set_obj.script_name == "":
        # 不存在
        print("script set not found")
        return

    if script_set_obj.status == SCRIPT_SET_STATUS_STOP:
        script_set_obj.run()
    else:
        print("script status is not STOP")


# ==============================================================================
#
# ==============================================================================
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

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        self.name = name
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
        self.script_obj_list = []
        self.script_name_list = []
        self.return_code_list = []
        self.status = SCRIPT_SET_STATUS_UNKNOWN

    def initial(self, name, script_name_list=None):
        """初始化一个新的对象"""
        self.name = name
        if script_name_list is not None:
            self.set_script(script_name_list)
        self.status = SCRIPT_SET_STATUS_STOP

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        self.name = name
        # 返回文件路径，使用sh执行
        conf_obj = ScriptSetConf(os.path.join(conf.PATH_SCRIPT_SET,
                                              self.name,
                                              "%s.conf" % self.name),
                                 self.name)
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj is None and conf_obj.get_name() is None:
            raise error.ScriptError(error.ERRNO_SCRIPT_OPENCONF_ERROR)
        conf_dict = conf_obj.load_config()
        self.script_name_list = conf_dict["script_name_list"]
        self.return_code_list = conf_dict["return_code_list"]
        self.stdout = conf_dict["status"]

    def save_conf(self):
        """保存配置到文件"""
        conf_dict = {
            "name": self.name,
            "script_name_list": self.script_name_list,
            "return_code_list": self.return_code_list,
            "status": self.status,
        }
        self.conf_obj.save_config(conf_dict)

    def set_script(self, script_name_list=None):
        """设置测试脚本"""
        if not isinstance(script_name_list, (list, tuple)):
            return
        self.script_name_list = list(script_name_list)

    def load_script(self):
        """从script name读取script信息出来"""
        script_obj_list = []
        for script_name in self.script_name_list:
            script_obj = Script()
            script_obj.load_conf(script_name)
            if script_obj.script_name != "":
                # 存在，可加进去
                script_obj_list.append(script_obj)
            else:
                print "add <%s> error. can't open conf file" % script_name
        self.script_obj_list = script_obj_list

    def run(self):
        """run scripts"""
        self.load_script()
        return_code_list = []
        for ts in self.script_obj_list:
            if isinstance(ts, Script):
                try:
                    exit_code = ts.run()
                    return_code_list.append(exit_code)
                except:
                    return_code_list.append("UnexpectedException")
            else:
                return_code_list.append("CommandFormatError")
        self.return_code_list = return_code_list
        return return_code_list

    def get_result(self):
        return self.return_code_list
