# coding:utf-8

# exception class

ERRNO_UNKNOWN_ERROR = 1000

ERRNO_SCRIPT_OPENCONF_ERROR = 1001


class ErleuchtenException(Exception):

    def __init__(self, errno=ERRNO_UNKNOWN_ERROR, msg=""):
        self.msg = msg

    def __repr__(self):
        return self.msg


class TestcaseError(ErleuchtenException):
    pass


class ScriptError(ErleuchtenException):
    pass


class CommandTimeoutError(Exception):
    pass


class FileLockException(Exception):
    pass
