# coding:utf-8

# process testing code
from erleuchten.environment import Environment
from erleuchten.environment import ENVVM_STATUS_UNKNOWN, ENVVM_STATUS_STOP, \
    ENVVM_STATUS_RUNNING
from erleuchten.script import ScriptSet
from erleucthen.util.error import TestcaseError


def check_name_exist(test_name):
    """"""


def create(args):
    """创建一个测试用例"""
    t = Testcase()
    t.initial(args.name)

def remove(args):
    """移除一个测试用例"""


class Testcase(object):
    """测试用例"""

    def __init__(self):
        self.name = ""
        # self.kwargs = kwargs
        self.env_obj = None                 # 测试环境
        self.prepare_script_set_obj = None  # 准备测试环境的脚本集合
        self.test_script_set_obj = None     # 测试脚本集合

    def initial(self, name, env_name=None, prepare_script_set_name=None,
                test_script_set_name=None):
        """"""
        self.name = name
        self.env_obj = Environment()
        self.prepare_script_set_obj = ScriptSet()
        self.test_script_set_obj = ScriptSet()

        if env_name:
            self.env_obj.initial(env_name)
        if prepare_script_set_name:
            self.prepare_script_set_obj .initial(prepare_script_set_name)
        if test_script_set_name:
            self.test_script_set_obj .initial(test_script_set_name)

    def process(self):
        """执行测试"""
        if self.env_obj.status == ENVVM_STATUS_UNKNOWN:
            # 测试机未就绪，不能测试
            raise TestcaseError("environment not ready")
        if self.env_obj.status == ENVVM_STATUS_STOP:
            # 环境没有开启，就打开环境
            self.env_obj.launch()

        if self.env_obj.status == ENVVM_STATUS_RUNNING:
            # 执行测试
            self.test_script_set_obj.run()
        else:
            raise TestcaseError("environment status unknown")

    def get_status(self):
        """获取测试的状态（目前做的到吗）"""


    def get_result(self):
        """获取测试结果（exit_code）"""

