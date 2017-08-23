# coding:utf-8

# test_script_class


# import time
import signal
import os
import subprocess
import shutil

from erleuchten.utils import conf
from erleuchten.utils.xml import ScriptConf, ScriptSetConf
from erleuchten.utils.util import create_dir
from erleuchten.utils.error import Errno, ErleuchtenException, \
    CommandTerminateError, CommandTimeoutError


# SCRIPT_STATUS_UNKNOWN = 'UNKNOWN'
# SCRIPT_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
# SCRIPT_STATUS_RUNNING = 'RUNNING'   # 运行状态

# SCRIPT_SET_STATUS_UNKNOWN = 'UNKNOWN'
# SCRIPT_SET_STATUS_STOP = 'STOP'         # 停止状态，随时可以执行
# SCRIPT_SET_STATUS_RUNNING = 'RUNNING'   # 运行状态

SCRIPT_RESULT_NO_SCRIPT = 'no_script'   # 没有脚本
SCRIPT_RESULT_SUCCEED = 'succeed'   # 脚本运行成功
SCRIPT_RESULT_BG_RUNNING = 'background_running'   # 脚本后台运行
SCRIPT_RESULT_NOT_A_SCRIPT = 'not a script'         # 加入了错误的脚本
SCRIPT_RESULT_ERROR_RETURNED = 'error_code_returned'    # 返回了非零的错误码
SCRIPT_RESULT_EXC_OCCUR = 'exception occured'    # 运行时候出现了异常


# ==============================================================================
#
# ==============================================================================
def create_script(name, script_path, appendix_path=[]):
    if os.path.exists(os.path.join(conf.get("PATH_SCRIPT"), name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPT_ALREADY_EXISTS)
        return

    script_obj = Script()
    script_obj.load_conf(name)

    script_obj.initial(name, script_path, appendix_path)
    script_obj.save_conf()
    print("<Script name: %s> created" % name)


def remove_script(name):
    if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT"), name,
                                       "%s.conf" % name)):
        # script不存在
        print("script {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPT_NOT_EXISTS)
        return
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_path != "":
        # 存在,可以删掉
        del script_obj
        shutil.rmtree(os.path.join(conf.get("PATH_SCRIPT"), name))
        print("remove script succeed")


def run_script(name):
    if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT"), name,
                                       "%s.conf" % name)):
        # script不存在
        print("script {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPT_NOT_EXISTS)
        return
    script_obj = Script()
    script_obj.load_conf(name)
    if script_obj.script_path == "":
        print("script not found")
        return
    print("script running")
    rtn_code = script_obj.run()
    print(rtn_code)


def list_script():
    if not os.path.exists(conf.get("PATH_SCRIPT")):
        create_dir(conf.get("PATH_SCRIPT"))
    result = []
    for i in os.listdir(conf.get("PATH_SCRIPT")):
        try:
            if os.path.isfile(os.path.join(conf.get("PATH_SCRIPT"), i,
                                           "%s.conf" % i)):
                result.append(i)
        except OSError:
            continue

    return result


# ==============================================================================
#
# ==============================================================================
def create_script_set(name, script_names):
    if os.path.exists(os.path.join(conf.get("PATH_SCRIPT_SET"), name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPTSET_ALREADY_EXISTS)
        return

    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)

    script_set_obj.initial(name, script_names)
    script_set_obj.save_conf()
    print("<Script-set name: %s> created" % name)


def set_script_set(name, script_names):
    if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT_SET"), name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPTSET_NOT_EXISTS)
        return

    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)

    script_set_obj.initial(name, script_names)
    script_set_obj.save_conf()
    print("set script-set succeed")


def remove_script_set(name, force=False):
    if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT_SET"), name,
                                       "%s.conf" % name)):
        # scriptset不存在
        print("script set {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPTSET_NOT_EXISTS)
        return

    shutil.rmtree(os.path.join(conf.get("PATH_SCRIPT_SET"), name))
    print("remove script-set succeed")


def run_script_set(name):
    if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT_SET"), name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPTSET_NOT_EXISTS)
        return

    script_set_obj = ScriptSet()
    script_set_obj.load_conf(name)

    print("script-set running")
    rtn_list = script_set_obj.run()
    return rtn_list


def list_script_set():
    if not os.path.exists(conf.get("PATH_SCRIPT_SET")):
        create_dir(conf.get("PATH_SCRIPT_SET"))
    result = []
    for i in os.listdir(conf.get("PATH_SCRIPT_SET")):
        try:
            if os.path.isfile(os.path.join(conf.get("PATH_SCRIPT_SET"), i,
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


def terminate_handler(signum, frame):
    """SIGTERM注册函数"""
    raise CommandTerminateError


class Script(object):
    """single test script"""

    def __init__(self):
        self.name = ""
        self.script_path = ""
        self.appendix = []
        self.pid = -1
        self.exceed_time = 0    # 超时时间
        self.stdout = None
        self.stderr = None
        self.conf_obj = None

    def initial(self, name, script_path, appendix_path=[],
                exceed_time=0, stdout=None):
        """初始化一个新的对象"""
        self.name = name
        self.set_script(script_path)
        self.set_appendix(appendix_path)
        # self.status = SCRIPT_STATUS_STOP
        self.exceed_time = exceed_time
        self.stdout = stdout

    def set_stdout(self, stdout):
        self.stdout = stdout

    def set_script(self, script_path):
        """将脚本复制进来"""
        create_dir(os.path.join(conf.get("PATH_SCRIPT"), self.name))
        filename = os.path.split(script_path)[1]
        new_path_name = os.path.join(conf.get("PATH_SCRIPT"), self.name,
                                     filename)
        shutil.copy(script_path, new_path_name)
        self.script_path = new_path_name

    def set_appendix(self, appendix_path_list):
        """将附加文件也复制进来, 与脚本放在一起"""
        create_dir(os.path.join(conf.get("PATH_SCRIPT"), self.name))
        for appendix_file in appendix_path_list:
            if not os.path.isfile(appendix_file):
                raise ErleuchtenException(
                    errno=Errno.ERRNO_APPENDIX_ONLY_SUPPORT_FILE)
            filename = os.path.split(appendix_file)[1]
            new_path_name = os.path.join(conf.get("PATH_SCRIPT"), self.name,
                                         filename)
            shutil.copy(appendix_file, new_path_name)

    def run_bg(self, stdout=None, stderr=None, append_env={}):
        """use os.fork to run program background
        使用fork在后台运行脚本。"""

        pid = os.fork()

        if pid == 0:
            return self.run(self, stdout, append_env)
        else:
            # 后台执行的话，返回PID给程序
            return pid

    def run(self, stdout=None, stderr=None, append_env={}):
        """run script
        根据不同的情况会返回不同类型的值(None，数字，字符串)"""
        if stdout is not None:
            self.stdout = stdout
        if stderr is not None:
            self.stderr = stderr
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.signal(signal.SIGTERM, terminate_handler)
        batch = os.path.join(conf.get("PATH_SCRIPT"), self.name,
                             self.script_path)
        cmd_list = [conf.get("SHELL_EXECUTOR"), batch]
        orig_cwd = os.getcwd()
        s_env = os.environ.copy()
        s_env.update(append_env)
        # 改变工作目录
        os.chdir(os.path.join(conf.get("PATH_SCRIPT"), self.name))
        try:
            signal.alarm(self.exceed_time)
            p = subprocess.Popen(cmd_list,
                                 stdout=self.stdout,
                                 stderr=self.stderr,
                                 env=s_env)
            self.pid = p.pid
            p.wait()
            exit_code = p.returncode
            signal.alarm(0)
            # print("exit_code is: %d" % exit_code)
            return exit_code
        except CommandTimeoutError:
            # 超时杀掉任务
            p.kill()
            return 142
        except CommandTerminateError:
            # 被终止杀掉任务
            p.kill()
            return 1

        finally:
            # 还原工作目录
            os.chdir(orig_cwd)

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        self.name = name
        conf_obj = ScriptConf(os.path.join(conf.get("PATH_SCRIPT"), self.name,
                                           "%s.conf" % self.name), self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj.xml_root_obj is None and conf_obj.get_name() is None:
            # raise ErleuchtenException(errno=Errno.ERRNO_XML_OPEN_CONF_FAILED)
            return
        conf_dict = conf_obj.load_config()
        self.script_path = conf_dict["script_path"]
        self.pid = int(conf_dict["pid"])
        self.exceed_time = int(conf_dict["exceed_time"])

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            # raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
            return
        conf_dict = {
            "name": self.name,
            "script_path": self.script_path,
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
        self.script_obj_list = []       # Script对象列表
        self.script_name_list = []      # 包含的Script名字列表
        self.script_prop_dict = {}      # script属性列表，{name:{prop1:val,},}
        # self.return_code_list = []      # 返回值列表
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
        conf_obj = ScriptSetConf(os.path.join(conf.get("PATH_SCRIPT_SET"),
                                              self.name,
                                              "%s.conf" % self.name),
                                 self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj is None and conf_obj.get_name() is None:
            # raise ErleuchtenException(errno=Errno.ERRNO_XML_OPEN_CONF_FAILED)
            return
        conf_dict = conf_obj.load_config()
        self.script_name_list = conf_dict.get("script_name_list", [])
        # self.return_code_list = conf_dict.get("return_code_list", [])

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            # raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
            return
        conf_dict = {
            "name": self.name,
            "script_name_list": self.script_name_list,
            # "return_code_list": self.return_code_list,
            "script_prop_dict": self.script_prop_dict,
        }
        self.conf_obj.save_config(conf_dict)

    def set_script(self, script_name_list=None):
        """设置测试脚本"""
        if not isinstance(script_name_list, (list, tuple)):
            return
        self.script_name_list = list(script_name_list)

    def set_script_prop(self, script_name, property_dict):
        """设置脚本集中脚本的属性，可设置
        background:1   允许后台执行"""
        d = self.script_prop_dict.get(script_name, {})
        d.update(property_dict)
        self.script_prop_dict[script_name] = d

    def load_script(self):
        """从script name读取script信息出来"""
        script_obj_list = []
        for script_name in self.script_name_list:
            script_obj = Script()
            script_obj.load_conf(script_name)
            if script_obj.script_path != "":
                # 存在，可加进去
                script_obj_list.append(script_obj)
            else:
                print("add <%s> error. can't open conf file. "
                      "will ignore it" % script_name)
        self.script_obj_list = script_obj_list

    def run(self, stdout=None, stderr=None, append_env={}):
        """按顺序运行脚本集中的脚本。
        如果脚本返回了成功，则继续执行下一个脚本，返回了其它的就中断"""
        self.load_script()

        # if stdout is not None:
        #     f_stdout = stdout
        # else:
        #     # 没有指定stdout的话，定义一个文件，写在test set配置文件目录下
        #     f_stdout = open(os.path.join(conf.get("PATH_SCRIPT_SET"),
        #                                  self.name, "%s.out" % self.name),
        #                                  'a+', 0)

        f_stdout = open(stdout, 'a+', 0)
        f_stderr = open(stderr, 'a+', 0)
        rtn_code = SCRIPT_RESULT_NO_SCRIPT
        for ts in self.script_obj_list:
            if isinstance(ts, Script):
                # 获取脚本属性
                d = self.script_prop_dict.get(ts.name, {})
                bg_run = d.get("background", 0)
                # 运行脚本
                try:
                    if bg_run:
                        ts.run_bg(stdout=f_stdout,
                                  stderr=f_stderr,
                                  append_env=append_env)
                        rtn_code = SCRIPT_RESULT_BG_RUNNING

                    else:
                        result = ts.run(stdout=f_stdout,
                                        stderr=f_stderr,
                                        append_env=append_env)
                        if result != 0:
                            # 返回非零，就是说，运行出错了
                            rtn_code = SCRIPT_RESULT_ERROR_RETURNED
                            break
                        else:
                            rtn_code = SCRIPT_RESULT_SUCCEED

                except:
                    rtn_code = SCRIPT_RESULT_EXC_OCCUR

        return rtn_code
