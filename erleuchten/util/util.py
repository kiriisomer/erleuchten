# coding:utf-8


import errno
import os
import stat
import random
import shutil

_DEFAULT_MODE = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO


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
        if exc.errno == errno.EEXIST:
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
        if e.errno != errno.ENOENT:
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
