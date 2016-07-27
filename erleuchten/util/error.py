# coding:utf-8

# exception class

ERRNO_UNKNOWN_ERROR = 1000

ERRNO_SCRIPT_OPENCONF_ERROR = 1001
ERRNO_SAVE_PATH_NOT_SPECIFY = 1002

ERRNO_XML_CANNOT_FIND_DISK = 2001


class ErleuchtenException(Exception):

    def __init__(self, errno=ERRNO_UNKNOWN_ERROR, msg=""):
        self.errno = errno
        self.msg = msg

    def __repr__(self):
        return self.errno


class TestcaseError(ErleuchtenException):
    pass


class ScriptError(ErleuchtenException):
    pass


class CommandTimeoutError(Exception):
    pass


class FileLockException(Exception):
    pass
