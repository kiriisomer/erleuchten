# coding:utf-8

# test_script_class


# import time
import signal
import subprocess

from erleuchten.util import conf


SCRIPT_STATUS_UNKNOWN = 'unknown'

SCRIPT_USAGE_UNKNOWN = 'unknown'


class CommandTimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise CommandTimeoutError


def process_command(cmd, exceed_time=0):
    """执行命令，等待命令完成。使用信号SIGALRM来处理超时状态"""
    signal.signal(signal.SIGALRM, timeout_handler)
    try:
        signal.alarm(exceed_time)
        cmd_list = [cmd]
        p = subprocess.Popen(cmd_list)
        p.wait()
        exit_code = p.returncode
        signal.alarm(0)
        return exit_code
    except CommandTimeoutError:
        p.kill()
        raise


class Script(object):
    """single test script"""

    def __init__(self):
        self.name = ""
        self.path = ""
        self.usage = SCRIPT_USAGE_UNKNOWN
        # self.pid = -1
        self.timeout = 0    # 超时时间
        self.status = SCRIPT_STATUS_UNKNOWN
        self.stdout = None

    def initial(self, name, path, timeout=0):
        self.name = name
        self.path = path
        self.timeout = timeout

    def run(self):
        """run script"""
        pass

    def get_command(self):
        """"""
        # 返回文件路径，使用sh执行
        return self.path

    def get_timeout(self):
        """"""
        return self.timeout

    def interrupt(self):
        """force stop script"""
        pass


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
        """add """
        self.script_list = script_list

    def run(self):
        """run scripts"""
        exit_code_list = []
        for ts in self.script_list:
            if isinstance(ts, Script):
                try:
                    exit_code = process_command(ts.get_command(),
                                                ts.get_timeout(),
                                                stdout=self.stdout,
                                                stderr=self.stderr)
                    exit_code_list.append(exit_code)
                except CommandTimeoutError:
                    exit_code_list.append("TimeExceed")

            exit_code_list.append("CommandFormatError")
        self.exit_code_list = exit_code_list
        return exit_code_list

    def get_result(self):
        return self.exit_code_list
