# coding:utf-8

# process testing code
from erleuchten import conf
from erleuchten.environment import Environment
from erleuchten.script import

def check_name_exist(test_name):
    """"""


def create_new_testcase(test_name):
    """"""


class Testcase(object):
    """testcase"""

    def __init__(self):
        self.name = ""
        # self.kwargs = kwargs

        self.env_obj = None                 # 测试环境
        self.test_script_set_obj = None     # 测试脚本集合

    def initial(self, name, env_name, test_script_set_name):
        """"""
        self.name = name
        self.env_obj = Environment(name)
        self.test_script_set_obj =


    def prepare(self):
        """prepare the environment"""


    def process(self):
        """"""

    def get_status(self):
        """"""

    def get_result(self):
        """"""
