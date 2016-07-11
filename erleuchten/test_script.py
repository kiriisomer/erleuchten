# coding:utf-8

# test_script_class


class TestScript(object):
    """single test script"""

    def __init__(self):
        self.name = ""
        self.path = ""
        self.pid = 0

    def run(self):
        """run script"""

    def interrupt(self):
        """force stop script"""


class TestScriptSet(object):
    """a series of test script"""
    def __init__(self):
        self.name = ""
        self.script_list = []

    def run(self):
        """run scripts"""
