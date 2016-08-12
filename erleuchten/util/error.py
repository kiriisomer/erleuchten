# coding:utf-8

# exception class


class Errno:
    ERRNO_UNKNOWN_ERROR = 1000

    ERRNO_OPENCONF_ERROR = 1001
    ERRNO_SAVE_PATH_NOT_SPECIFY = 1002
    ERRNO_CANNOT_FIND_VM_IN_ENV = 1003
    ERRNO_APPENDIX_ONLY_SUPPORT_FILE = 1004

    ERRNO_XML_CANNOT_FIND_DISK = 2001
    ERRNO_XML_CANNOT_FIND_INTERFACE = 2002
    ERRNO_XML_CANNOT_FIND_DOMAIN_NAME = 2003
    ERRNO_XML_CANNOT_FIND_DOMAIN_UUID = 2004
    ERRNO_XML_DONAMIN_UUID_CONFLICT = 2005
    ERRNO_XML_DONAMIN_NAME_CONFLICT = 2006

    ERROR_UTIL_ACQUIRE_LOCK_FAILED = 3001


class ErleuchtenException(Exception):

    def __init__(self, errno=Errno.ERRNO_UNKNOWN_ERROR, other_msg=""):
        self.errno = errno
        self.other_msg = other_msg

    def __str__(self):
        return self.errno


class FileLockException(Exception):
    pass
