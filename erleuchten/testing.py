# coding:utf-8

# process testing code
from erleuchten import conf


def check_name_exist(test_name):
    """"""


def create_new_testcase(test_name):
    """"""


class Testcase(object):
    """testcase"""

    def __init__(self, name, **kwargs):
        self.name = name
        self.kwargs = kwargs

        self.env_name = ""          # 测试环境名字
        self.test_script = ""       # 测试脚本路径
        self.except_script = ""     # 异常脚本路径

    def prepare(self):
        """"""

    def process(self):
        """"""

    def get_status(self):
        """"""

    def get_result(self):
        """"""
