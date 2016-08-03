# coding:utf-8

# test_script_class


# import time
import signal
import os
import subprocess
import shutil

from erleuchten.util import conf
from erleuchten.util.xml import ScriptConf, ScriptSetConf
from erleuchten.util.util import create_dir
from erleuchten.util.error import Errno, ErleuchtenException


SCRIPT_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_STATUS_RUNNING = 'RUNNING'   # 运行状态

SCRIPT_SET_STATUS_UNKNOWN = 'UNKNOWN'
SCRIPT_SET_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
SCRIPT_SET_STATUS_RUNNING = 'RUNNING'   # 运行状态


class CommandTimeoutError(Exception):
    """执行命令专用异常，用于捕捉超时"""
    pass


# ==============================================================================
#
# ==============================================================================
def create_script(name, script_name, appendix_path=[]):
    if os.path.exists(os.path.join(conf.PATH_SCRIPT, name, "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(name))
        return

    script_obj = Script()
    script_obj.load_conf(name)

    script_obj.initial(name, script_name, appendix_path)
    script_obj.save_conf()


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

    rtn_code = script_obj.run()
    print(rtn_code)


def list_script():
    if not os.path.exists(conf.PATH_SCRIPT):
        create_dir(conf.PATH_SCRIPT)
    result = []
    for i in os.listdir(conf.PATH_SCRIPT):
        try:
            if os.path.isfile(os.path.join(conf.PATH_SCRIPT, i,
                                           "%s.conf" % i)):
                result.append(i)
        except OSError:
            continue

    return result


# ==============================================================================
#
# ==============================================================================
def create_script_set(name, script_names):
    if os.path.exists(os.path.join(conf.PATH_SCRIPT_SET, name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("name already existed")
        return

    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)

    script_set_obj.initial(name, script_names)
    script_set_obj.save_conf()


def set_script_set(name, script_names):
    if not os.path.exists(os.path.join(conf.PATH_SCRIPT_SET, name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set not found")
        return

    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)

    script_set_obj.initial(name, script_names)
    script_set_obj.save_conf()


def remove_script_set(name, force=False):
    shutil.rmtree(os.path.join(conf.PATH_SCRIPT_SET, name))


def run_script_set(name):
    if not os.path.exists(os.path.join(conf.PATH_SCRIPT_SET, name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set not found")
        return

    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)

    rtn_list = script_set_obj.run()
    print '\n'.join(rtn_list)


def list_script_set():
    if not os.path.exists(conf.PATH_SCRIPT_SET):
        create_dir(conf.PATH_SCRIPT_SET)
    result = []
    for i in os.listdir(conf.PATH_SCRIPT_SET):
        try:
            if os.path.isfile(os.path.join(conf.PATH_SCRIPT_SET, i,
                                           "%s.conf" % i)):
                result.append(i)
        except OSError:
            continue

    return result


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
        self.appendix = []
        self.pid = -1
        self.exceed_time = 0    # 超时时间
        self.stdout = None
        self.conf_obj = None

    def initial(self, name, script_name, appendix_path=[],
                exceed_time=0, stdout=None):
        """初始化一个新的对象"""
        self.name = name
        self.set_script(script_name)
        self.set_appendix(appendix_path)
        # self.status = SCRIPT_STATUS_STOP
        self.exceed_time = exceed_time
        self.stdout = stdout

    def set_stdout(self, stdout):
        self.stdout = stdout

    def set_script(self, script_name):
        """将脚本复制进来"""
        create_dir(os.path.join(conf.PATH_SCRIPT, self.name))
        filename = os.path.split(script_name)[1]
        new_path_name = os.path.join(conf.PATH_SCRIPT, self.name, filename)
        shutil.copy(script_name, new_path_name)
        self.script_name = new_path_name

    def set_appendix(self, appendix_path_list):
        """将附加文件也复制进来, 与脚本放在一起"""
        create_dir(os.path.join(conf.PATH_SCRIPT, self.name))
        for appendix_file in appendix_path_list:
            if not os.path.isfile(i):
                raise ErleuchtenException(
                    errno=Errno.ERRNO_APPENDIX_ONLY_SUPPORT_FILE)
            filename = os.path.split(appendix_file)[1]
            new_path_name = os.path.join(conf.PATH_SCRIPT, self.name, filename)
            shutil.copy(appendix_file, new_path_name)

    def run(self, stdout=None):
        """run script
        根据不同的情况会返回不同类型的值(None，数字，字符串)"""
        if stdout is not None:
            self.stdout = stdout
        signal.signal(signal.SIGALRM, timeout_handler)
        batch = os.path.join(conf.PATH_SCRIPT, self.name, self.script_name)
        cmd_list = [conf.SHELL_EXECUTOR, batch]
        orig_cwd = os.getcwd()
        os.chdir(os.path.join(conf.PATH_SCRIPT, self.name))
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
        finally:
            os.chdir(orig_cwd)

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        self.name = name
        conf_obj = ScriptConf(os.path.join(conf.PATH_SCRIPT, self.name,
                                           "%s.conf" % self.name), self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj.xml_root_obj is None and conf_obj.get_name() is None:
            return
        conf_dict = conf_obj.load_config()
        self.script_name = conf_dict["script_name"]
        self.pid = int(conf_dict["pid"])
        self.exceed_time = int(conf_dict["exceed_time"])

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        conf_dict = {
            "name": self.name,
            "script_name": self.script_name,
            "pid": self.pid,
            "exceed_time": self.exceed_time,
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
        self.conf_obj = None

    def initial(self, name, script_name_list=None):
        """初始化一个新的对象"""
        self.name = name
        if script_name_list is not None:
            self.set_script(script_name_list)

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        self.name = name
        # 返回文件路径，使用sh执行
        conf_obj = ScriptSetConf(os.path.join(conf.PATH_SCRIPT_SET,
                                              self.name,
                                              "%s.conf" % self.name),
                                 self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj is None and conf_obj.get_name() is None:
            return
        conf_dict = conf_obj.load_config()
        self.script_name_list = conf_dict.get("script_name_list", [])
        self.return_code_list = conf_dict.get("return_code_list", [])

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        conf_dict = {
            "name": self.name,
            "script_name_list": self.script_name_list,
            "return_code_list": self.return_code_list,
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
                print ("add <%s> error. can't open conf file. "
                       "will ignore it" % script_name)
        self.script_obj_list = script_obj_list

    def run(self):
        """run scripts"""
        self.load_script()
        f_stdout = open(os.path.join(conf.PATH_SCRIPT_SET, self.name,
                                     "%s.out" % self.name), 'a+', 0)
        return_code_list = []
        for ts in self.script_obj_list:
            if isinstance(ts, Script):
                try:
                    exit_code = ts.run(stdout=f_stdout)
                    return_code_list.append(str(exit_code))
                except:
                    return_code_list.append("UnexpectedException")
            else:
                return_code_list.append("CommandFormatError")
        self.return_code_list = return_code_list
        return return_code_list

    def get_result(self):
        return self.return_code_list
