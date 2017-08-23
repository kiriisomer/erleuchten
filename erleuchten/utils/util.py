# coding:utf-8


import errno as sys_errno
import os
import stat
import random
import shutil
import fcntl

from contextlib import contextmanager

from erleuchten.utils.error import ErleuchtenException
from erleuchten.utils.error import Errno

_DEFAULT_MODE = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO


def lock_fp(fp):
    try:
        fcntl.flock(fp, fcntl.LOCK_EX)
    except IOError:
        raise ErleuchtenException(Errno.ERROR_UTIL_ACQUIRE_LOCK_FAILED)


def unlock_fp(fp):
    fcntl.flock(fp, fcntl.LOCK_UN)


@contextmanager
def make_file_lock(fp):
    lock_fp(fp)
    try:
        yield
    except RuntimeError:
        raise
    finally:
        unlock_fp(fp)


def ramdom_mac_addr(orig_mac_list=[]):
    while 1:
        new_mac = ":".join(['52', '12', '00', '%02x' % random.randint(0, 255),
                            '%02x' % random.randint(0, 255),
                            '%02x' % random.randint(0, 255)])
        if new_mac in orig_mac_list:
            continue
        else:
            return new_mac


def create_file_path(path, mode=_DEFAULT_MODE):
    create_dir(os.path.split(path)[0], mode)


def create_dir(path, mode=_DEFAULT_MODE):
    """Create a directory (and any ancestor directories required)

    :param path: Directory to create
    :param mode: Directory creation permissions
    """
    try:
        os.makedirs(path, mode)
    except OSError as exc:
        if exc.errno == sys_errno.EEXIST:
            if not os.path.isdir(path):
                raise
        else:
            raise


def delete_if_exists(path, remove=os.unlink):
    """Delete a file, but ignore file not found error.

    :param path: File to delete
    :param remove: Optional function to remove passed path
    """

    try:
        remove(path)
    except OSError as e:
        if e.errno != sys_errno.ENOENT:
            raise


def copy_file(src, tgt):
    """复制文件，不存在目录的话，新建一个"""
    # 判断输入的路径是目录还是文件
    if tgt[-1] == os.path.sep:
        if not os.path.exists(tgt):
            # 不存在目录的话，新建一个
            create_dir(tgt)
    else:
        if not os.path.exists(os.path.split(tgt)[0]):
            # 不存在目录的话，新建一个
            create_file_path(tgt)

    return shutil.copy(src, tgt)
