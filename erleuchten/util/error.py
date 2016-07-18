# coding:utf-8

# exception class

ERRNO_UNKNOWN_ERROR = 1000


class TestcaseError(Exception):
    def __init__(self, errno=ERRNO_UNKNOWN_ERROR, msg=""):
        self.msg = msg

    def __repr__(self):
        return self.msg


class CommandTimeoutError(Exception):
    pass
