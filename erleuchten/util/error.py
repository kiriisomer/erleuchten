# coding:utf-8

# exception class


class TestcaseError(Exception):
    def __init__(self, msg):
        self.msg

    def __repr__(self):
        return self.msg


class CommandTimeoutError(Exception):
    pass
