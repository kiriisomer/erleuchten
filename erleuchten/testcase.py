# coding:utf-8

# process testing code

import time
import os
import shutil
import pickle
from multiprocessing import Pool

from erleuchten import environment
from erleuchten.environment import Environment
from erleuchten.script import ScriptSet
from erleuchten.script import SCRIPT_RESULT_SUCCEED, \
    SCRIPT_RESULT_ERROR_RETURNED, SCRIPT_RESULT_EXC_OCCUR

from erleuchten.utils import conf
from erleuchten.utils.xml import TestcaseConf
from erleuchten.utils.error import ErleuchtenException, Errno, CommandTerminateError
from erleuchten.utils.util import create_dir, make_file_lock


TESTCASE_STATUS_STOP_AND_NOT_PREPARE = 'testcase_status_stop_and_not_prepare'
TESTCASE_STATUS_PREPARING = 'testcase_status_preparing'
TESTCASE_STATUS_STOP = 'testcase_status_stop'
TESTCASE_STATUS_TERMINATED = 'testcase_status_terminated'
TESTCASE_STATUS_RUNNING = 'testcase_status_running'

ENV_STATUS_RUNNING = 'running'

# 测试用的环境变量字典模板，传递给测试脚本
SCRIPT_ENV_DICT = {"ERLEUCHTEN_ENVIRONMENT_NAME": "",
                   "ERLEUCHTEN_SCRIPTSET_NAME": ""}


def blabla(scriptset_obj, out_going, err_going, env_ing):
    env_ing["ERLEUCHTEN_SCRIPTSET_NAME"] = scriptset_obj.name
    rtn = scriptset_obj.run(out_going, err_going, env_ing)
    return rtn


def terminate_handler(signum, frame):
    """SIGTERM注册函数"""
    raise CommandTerminateError


def create(name, env_name=None, init_scriptset=None, test_scriptset=[]):
    """创建一个测试用例"""
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), env_name,
                                       "%s.conf" % env_name)):
        # env不存在
        print("env {name} not found".format(**{'name': env_name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_ENV_NOT_EXISTS)
        return

    if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT_SET"),
                                       init_scriptset,
                                       "%s.conf" % init_scriptset)):
        # init_scriptset不存在
        print("script set {name} not found".format(**{'name': init_scriptset}))
        raise ErleuchtenException(errno=Errno.ERRNO_SCRIPTSET_NOT_EXISTS)
        return

    for i in test_scriptset:
        if not os.path.exists(os.path.join(conf.get("PATH_SCRIPT_SET"), i,
                                           "%s.conf" % i)):
            # test_scriptset不存在
            print("script set {name} not found".format(**{'name': i}))
            raise ErleuchtenException(errno=Errno.ERRNO_SCRIPTSET_NOT_EXISTS)
            return

    if os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_ALREADY_EXISTS)
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    testcase_obj.initial(name, env_name, init_scriptset, test_scriptset)
    testcase_obj.save_conf()
    print("<Testcase name: %s> created" % name)


def modify(name, env_name=None, init_scriptset=None, test_scriptset=[]):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)

    testcase_obj.initial(name, env_name, init_scriptset, test_scriptset)
    testcase_obj.save_conf()
    print("modify testcase succeed")


def init_env(name):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    testcase_obj.status = TESTCASE_STATUS_STOP_AND_NOT_PREPARE
    testcase_obj.init_env()
    testcase_obj.prepare()
    testcase_obj.save_conf()
    print("<Env name: %s> initialized (inside init_env)" % name)


def start(name, background=False):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    if background:
        print("test start")
        testcase_obj.start_test_bg()
    else:
        print("test start")
        testcase_obj.start_test()
    testcase_obj.save_conf()


def stop(name):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)

    testcase_obj.stop_process()
    print("test stopped")
    testcase_obj.save_conf()


def remove(name):
    """移除一个测试用例"""
    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    if testcase_obj.name != "":
        # 存在,可以删掉
        del testcase_obj
        shutil.rmtree(os.path.join(conf.get("PATH_TESTCASE"), name))
        print("remove testcase succeed")
    else:
        print("testcase not exists")


def list_testcase():
    if not os.path.exists(conf.get("PATH_TESTCASE")):
        create_dir(conf.get("PATH_TESTCASE"))
    result = []
    for i in os.listdir(conf.get("PATH_TESTCASE")):
        try:
            if os.path.isfile(os.path.join(conf.get("PATH_TESTCASE"), i,
                                           "%s.conf" % i)):
                result.append(i)
        except OSError:
            continue

    return result


def set_scriptset_prop(name, scriptset_name, background=0):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return

    prop_dict = {'background': background}
    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    testcase_obj.set_scriptset_prop(scriptset_name, prop_dict)
    print("set scriptest prop succeed")
    testcase_obj.save_conf()


def get_status(name):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return
    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    return testcase_obj.get_status()


def get_result(name):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # testcase不存在
        print("testcase {name} not found".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_TESTCASE_NOT_EXISTS)
        return
    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    return testcase_obj.get_result()


class Testcase(object):
    """测试用例"""

    def __init__(self):
        self.name = ""
        # self.kwargs = kwargs
        self.status = TESTCASE_STATUS_STOP_AND_NOT_PREPARE    # 状态，用于区分是否在运行脚本
        self.pidlist = []                     # testcase运行的pid
        self.env_name = None                  # 测试环境名
        self.env_obj = None                   # 测试环境
        self.test_scriptset_name_list = []    # 测试脚本集名字列表
        self.test_scriptset_obj_list = []     # 测试脚本对象列表
        self.scriptset_prop_dict = {}         # 测试脚本对象列表
        self.prepare_scriptset_name = ""      # 准备测试环境的脚本集名字
        self.prepare_scriptset_obj = None     # 准备测试环境的脚本集对象
        self.conf_obj = None

        self.start_time = ""        # 测试开始时间
        self.stop_time = ""         # 测试结束时间
        self.result = "no_result"   # 最终测试结果
        self.result_dict = {}       # 记录每次测试结果{set_name: result}

    def initial(self, name, env_name=None, prepare_scriptset_name=None,
                test_scriptset_name_list=[]):
        """根据名字获取测试用例的信息"""
        self.name = name
        self.test_scriptset_name_list = []
        self.test_scriptset_obj_list = []

        if env_name:
            self.env_name = env_name
            self.env_obj = Environment()
            self.env_obj.load_conf(env_name)
        if prepare_scriptset_name:
            self.prepare_scriptset_name = prepare_scriptset_name
            self.prepare_scriptset_obj = ScriptSet()
            self.prepare_scriptset_obj.load_conf(prepare_scriptset_name)
        if test_scriptset_name_list:
            self.test_scriptset_name_list = test_scriptset_name_list
            for i in test_scriptset_name_list:
                ss = ScriptSet()
                ss.load_conf(i)
                self.test_scriptset_obj_list.append(ss)

    def init_env(self):
        """初始化环境，开机，然后运行初始化脚本"""
        self.env_obj.initial_all_vm()

    def set_scriptset_prop(self, scriptset_name, property_dict):
        """设置脚本集的属性，可设置
        background:1   允许后台执行"""
        d = self.scriptset_prop_dict.get(scriptset_name, {})
        d.update(property_dict)
        self.scriptset_prop_dict[scriptset_name] = d

    def prepare(self, stdout=None, stderr=None, append_env={}):
        """准备环境"""
        if self.status == TESTCASE_STATUS_STOP_AND_NOT_PREPARE:
            if self.env_obj.status != ENV_STATUS_RUNNING:
                #     # 环境没有开启，就打开环境
                # 尝试打开环境里的虚拟机
                environment.env_start(self.env_name)
                self.env_obj.load_conf(self.env_name)

            if self.env_obj.status == ENV_STATUS_RUNNING:
                # 设置stdout
                # if stdout is not None:
                #     f_stdout = stdout
                # else:
                # 没有指定stdout的话，定义一个文件，写在test set配置文件目录下
                #     f_stdout = open(os.path.join(conf.get("PATH_TESTCASE"),
                #                                  "%s.out" % self.name),
                #                                  'a+', 0)
                # 设置环境变量
                f_env = SCRIPT_ENV_DICT
                f_env["ERLEUCHTEN_ENVIRONMENT_NAME"] = self.env_name
                f_env["ERLEUCHTEN_SCRIPTSET_NAME"] = \
                    self.prepare_scriptset_obj.name
                f_env.update(append_env)

                # 执行准备环境的脚本
                self.status = TESTCASE_STATUS_PREPARING
                self.save_conf()
                out_path = os.path.join(conf.get("PATH_TESTCASE"),
                                        self.name, "%s.out" % self.name)
                err_path = os.path.join(conf.get("PATH_TESTCASE"),
                                        self.name, "%s.err" % self.name)
                print("   Output is at: %s" % out_path)
                print("Error log is at: %s" % err_path)
                try:
                    result = self.prepare_scriptset_obj.run(out_path,
                                                            err_path,
                                                            append_env=f_env)
                    if result != SCRIPT_RESULT_SUCCEED:
                        raise ErleuchtenException(
                            errno=Errno.ERROR_SCRIPT_RETURN_FAIL)
                finally:
                    self.status = TESTCASE_STATUS_STOP
                    self.save_conf()
            else:
                raise ErleuchtenException(errno=Errno.ERROR_UNKNOWN_ENV_STATUS)

    def start_test_bg(self, stdout=None, append_env={}):
        """使用fork在后台运行脚本。"""

        pid = os.fork()

        if pid == 0:
            return self.start_test(stdout, append_env)
        else:
            # 后台执行的话，返回PID给程序
            return pid

    def start_test(self, stdout=None, append_env={}):
        """执行测试"""
        if self.status == TESTCASE_STATUS_RUNNING:
            # 这个脚本的状态是正在运行，报错。
            raise ErleuchtenException(errno=Errno.ERROR_TESTCASE_RUNNING)

        if self.env_obj.status != ENV_STATUS_RUNNING:
            #     # 环境没有开启，就打开环境
            # 尝试打开环境里的虚拟机
            environment.env_start(self.env_name)
            self.env_obj.load_conf(self.env_name)

        if self.env_obj.status == ENV_STATUS_RUNNING:
            # 执行测试
            self.status = TESTCASE_STATUS_RUNNING
            self.save_conf()
            self._init_testset_file()
            self.start_time = time.strftime('%Y%m%d_%X', time.localtime())
            # try:
            self._process(stdout=None, append_env={})
            # finally:
            self._collect_result()

        else:
            raise ErleuchtenException(errno=Errno.ERROR_UNKNOWN_ENV_STATUS)

    def _process(self, stdout=None, append_env={}):
        """执行代码"""
        # 设置stdout
        # if stdout is not None:
        #     f_stdout = stdout
        # else:
        #     # 没有指定stdout的话，定义一个文件，写在test set配置文件目录下
        #     f_stdout = open(os.path.join(conf.get("PATH_TESTCASE"),
        #                                  self.name, "%s.out" % self.name),
        #                     'a+', 0)
        # 设置环境变量
        f_env = SCRIPT_ENV_DICT
        f_env["ERLEUCHTEN_ENVIRONMENT_NAME"] = self.env_name
        f_env.update(append_env)
        # 设置自己的pid
        pid = os.getpid()
        with open("/tmp/erleuchten-testcase.lock", 'a+') as fp:
            with make_file_lock(fp):
                self.load_conf(self.name)
                self.pidlist.append(str(pid))
                self.save_conf()

        result = SCRIPT_RESULT_SUCCEED

        out_path = os.path.join(conf.get("PATH_TESTCASE"),
                                self.name, "%s.out" % self.name)
        err_path = os.path.join(conf.get("PATH_TESTCASE"),
                                self.name, "%s.err" % self.name)
        print("   Output is at: %s" % out_path)
        print("Error log is at: %s" % err_path)
        num_of_set = len(self.test_scriptset_obj_list)

        bg_scriptset_list = []
        bg_tag_list = []
        bg_pool = Pool(processes=num_of_set)
        res = []
        for i in self.test_scriptset_obj_list:
            if isinstance(i, ScriptSet):
                pool = Pool(processes=1)
                d = self.scriptset_prop_dict.get(i.name, {})
                bg_run = d.get("background", 0)
                if bg_run:
                    print("\n<Set: {0}> to background".format(i.name))
                    res.append(bg_pool.apply_async(blabla,
                               args=(i, out_path, err_path, f_env, )))
                    bg_scriptset_list.append(pool)
                    bg_tag_list.append(i)
                    print("Continue...\n")
                    continue
                res.append(pool.apply_async(blabla,
                           args=(i, out_path, err_path, f_env, )))
                print("\nWaitting for <Set: {0}> to end".format(i.name))
                pool.close()
                pool.join()
        print("\nWaitting for the processes in background to end")
        bg_pool.close()
        bg_pool.join()
        print("Getting results...")
        for i in range(0, num_of_set):
            if isinstance(self.test_scriptset_obj_list[i], ScriptSet):
                temp = res[i].get(timeout=300)
                self.result_dict[self.test_scriptset_obj_list[i].name] = temp
                print("{0}: {1}".format(self.test_scriptset_obj_list[i].name,
                                        temp))
        print("Processes done...")
        self.result = result

    def stop_process(self):
        """使用记载的pid杀掉进程"""
        for pid in self.pidlist:
            try:
                os.kill(int(pid))
            except:
                pass
        self.status = TESTCASE_STATUS_TERMINATED

    def get_status(self):
        """获取测试的状态"""
        if self.status is None:
            raise ErleuchtenException(errno=Errno.ERROR_TESTCASE_STATUS_IS_NONE)
        status = self.status
        return status

    def _collect_result(self):
        """运行结束后收集结果"""
        self._read_testset_file()
        # 检查结果里有没有失败，有失败的话就是运行失败了，测试也结束了。
        for sn, sr in self.result_dict.items():
            if sr in [SCRIPT_RESULT_ERROR_RETURNED, SCRIPT_RESULT_EXC_OCCUR]:
                self.result = sr

        self.stop_time = time.strftime('%Y%m%d_%X', time.localtime())
        self._save_result()
        self.status = TESTCASE_STATUS_STOP
        self.save_conf()

    def _save_result(self):
        """每次运行testset结束后保存运行结果"""
        path = os.path.join(conf.get("PATH_TESTCASE"),
                            self.name, "result.txt")
        with open(path, 'a+') as fp:
            with make_file_lock(fp):
                fp.write("  ".join([self.start_time, self.stop_time,
                                    self.result]))
                fp.write("\n")

    def _write_testset_to_file(self):
        """将测试概要写进testset_running_info.txt中"""
        path = os.path.join(conf.get("PATH_TESTCASE"),
                            self.name, "testset_running_info.txt")

        with open("/tmp/erleuchten-testcase.lock", 'a+') as fp:
            try:
                with open(path, 'rb') as fp:
                    with make_file_lock(fp):
                        temp = pickle.load(fp)
                        temp.update(self.result_dict)
                        self.result_dict = temp
            except IOError:
                # 文件不存在，打不开
                pass
            with open(path, 'wb') as fp:
                with make_file_lock(fp):
                    pickle.dump(self.result_dict, fp)

    def _read_testset_file(self):
        """读取testset_running_info.txt"""
        path = os.path.join(conf.get("PATH_TESTCASE"),
                            self.name, "testset_running_info.txt")
        try:
            with open(path, 'rb') as fp:
                with make_file_lock(fp):
                    self.result_dict = pickle.load(fp)
        except IOError:
            # 文件不存在，打不开
            pass

    def _init_testset_file(self):
        path = os.path.join(conf.get("PATH_TESTCASE"),
                            self.name, "testset_running_info.txt")
        try:
            os.remove(path)
        except OSError:
            pass
        self.pidlist = []
        self.save_conf()

    def get_result(self):
        """获取测试结果（exit_code）"""
        if self.status == TESTCASE_STATUS_STOP:
            path = os.path.join(conf.get("PATH_TESTCASE"),
                                self.name, "result.txt")
            try:
                with open(path, 'rb') as fp:
                    with make_file_lock(fp):
                        result = fp.read()
                        return result
            except IOError:
                pass
        else:
            raise ErleuchtenException(errno=Errno.ERROR_TESTCASE_STATUS_IS_WRONG)

    def load_conf(self, name):
        self.name = name
        conf_obj = TestcaseConf(os.path.join(conf.get("PATH_TESTCASE"),
                                             self.name, "%s.conf" % self.name),
                                self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj is None and conf_obj.get_name() is None:
            return
        conf_dict = conf_obj.load_config()
        self.status = conf_dict.get("status", "")
        self.env_name = conf_dict.get("env_name", "")
        self.pidlist = conf_dict.get("pidlist", "").split('-')
        self.prepare_scriptset_name = conf_dict.get(
            "prepare_scriptset_name", "")
        self.test_scriptset_name_list = conf_dict.get(
            "test_scriptset_name_list", [])
        self.scriptset_prop_dict = conf_dict.get(
            "scriptset_prop_dict", {})
        # 读取完毕后，初始化一下自己
        self.initial(name, self.env_name, self.prepare_scriptset_name,
                     self.test_scriptset_name_list)

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        conf_dict = {
            "status": self.status,
            "env_name": self.env_name,
            "pidlist": "-".join(self.pidlist),
            "prepare_scriptset_name": self.prepare_scriptset_name,
            "test_scriptset_name_list": self.test_scriptset_name_list,
            "scriptset_prop_dict": self.scriptset_prop_dict,
        }
        self.conf_obj.save_config(conf_dict)
