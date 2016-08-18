# coding:utf-8

# process testing code

import os
import shutil

from erleuchten.environment import Environment
from erleuchten.environment import ENVVM_STATUS_UNKNOWN, ENVVM_STATUS_STOP, \
    ENVVM_STATUS_RUNNING
from erleuchten.script import ScriptSet
from erleuchten.script import SCRIPT_RESULT_SUCCEED

from erleuchten.util import conf
from erleucthen.util.error import ErleuchtenException, Errno


def create(name, env_name=None, init_scriptset=None, test_scriptset=[]):
    """创建一个测试用例"""
    if os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(name))
        return

    testcase_obj = Testcase()
    # testcase_obj.load_conf(name)
    testcase_obj.initial(name)
    testcase_obj.save_conf()


def modify(name, env_name=None, init_scriptset=None, test_scriptset=[]):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set {name} not found".format(name))
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)

    testcase_obj.initial(name, env_name, init_scriptset, test_scriptset)
    testcase_obj.save_conf()


def init_env(name):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set not found")
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)

    testcase_obj.init_env()


def start(name):
    if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
                                       "%s.conf" % name)):
        # script set不存在
        print("script set not found")
        return

    testcase_obj = Testcase()
    testcase_obj.load_conf(name)

    testcase_obj.process()


def stop(name):
    pass
    # if not os.path.exists(os.path.join(conf.get("PATH_TESTCASE"), name,
    #                                    "%s.conf" % name)):
    #     # script set不存在
    #     print("script set not found")
    #     return

    # testcase_obj = Testcase()
    # testcase_obj.load_conf(name)

    # testcase_obj.init_env()


def remove(name):
    """移除一个测试用例"""
    testcase_obj = Testcase()
    testcase_obj.load_conf(name)
    if testcase_obj.name != "":
        # 存在,可以删掉
        del testcase_obj
        shutil.rmtree(os.path.join(conf.get("PATH_TESTCASE"), name))


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


class Testcase(object):
    """测试用例"""

    def __init__(self):
        self.name = ""
        # self.kwargs = kwargs
        self.env_name = None                  # 测试环境名
        self.env_obj = None                   # 测试环境
        self.test_scriptset_name_list = []    # 测试脚本集名字列表
        self.test_scriptset_obj_list = []     # 测试脚本对象列表
        self.prepare_script_set_name = ""     # 准备测试环境的脚本集名字
        self.prepare_script_set_obj = None    # 准备测试环境的脚本集对象
        self.conf_obj = None
        self.testinfo

    def initial(self, name, env_name=None, prepare_script_set_name=None,
                test_script_set_name=None):
        """根据名字获取测试用例的信息"""
        self.name = name
        self.env_obj = Environment()
        self.prepare_script_set_obj = ScriptSet()
        self.test_scriptset_name_list = ScriptSet()

        if env_name:
            self.env_obj.initial(env_name)
        if prepare_script_set_name:
            self.prepare_script_set_obj .initial(prepare_script_set_name)
        if test_script_set_name:
            self.test_script_set_obj.initial(test_script_set_name)

    def init_env(self):
        """初始化环境，开机，然后运行初始化脚本"""
        pass

    def start_test_bg(self):
        """使用fork在后台运行脚本。"""

        pid = os.fork()

        if pid == 0:
            return self.start_test(self)
        else:
            # 后台执行的话，返回PID给程序
            return pid

    def start_test(self):
        """执行测试"""
        if self.env_obj.status == ENVVM_STATUS_STOP:
            # 环境没有开启，就打开环境
            self.env_obj.launch()

        elif self.env_obj.status == ENVVM_STATUS_RUNNING:
            # 执行测试
            self.process()
            # self.test_script_set_obj.run()
        else:
            raise ErleuchtenException(Errno.ERROR_UNKNOWN_ENV_STATUS)

    def process(self):
        """执行测试"""
        for i in self.prepare_script_set_obj:
            result = i.run()
            if result != SCRIPT_RESULT_SUCCEED:
                # 没有返回正确，
                break

    def get_status(self):
        """获取测试的状态（目前做的到吗）"""

    def get_result(self):
        """获取测试结果（exit_code）"""
        return self.test_script_set_obj.get_result()

    def delete(self):
        """删除测试用例"""

    def load_conf(self):
        pass

    def save_cond(self):
        pass

