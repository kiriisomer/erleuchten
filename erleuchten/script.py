# coding:utf-8

# test_script_class


# import time
import signal
import os
import subprocess

from erleuchten.util import conf
from erleuchten.util.xml import ScriptConf


SHELL_EXECUTOR = '/bin/sh'


SCRIPT_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_STATUS_NEW = 'NEW'           # 新对象，没有配置文件
SCRIPT_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_STATUS_RUNNING = 'RUNNING'   # 运行状态


class CommandTimeoutError(Exception):
    pass


class FileLockException(Exception):
    pass


def timeout_handler(signum, frame):
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

    def initial(self, name):
        """从文件名获取配置文件，读取测试的属性"""
        self.name = name
        self.open_conf()

    def set_stdout(self, stdout):
        self.stdout = stdout

    def run(self):
        """run script
        根据不同的情况会返回不同类型的值"""
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

    def open_conf(self):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        conf_obj = ScriptConf(os.path.join(conf.PATH_SCRIPT, self.name,
                                           "%s.conf" % self.name))
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj is None and conf_obj.get_name() is None:
            return

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

    def get_timeout(self):
        """"""
        return self.exceed_time

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
                except CommandTimeoutError:
                    exit_code_list.append("TimeExceed")
            else:
                exit_code_list.append("CommandFormatError")
        self.exit_code_list = exit_code_list
        return exit_code_list

    def get_result(self):
        return self.exit_code_list
