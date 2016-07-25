# coding:utf-8


import errno
import os
import stat


_DEFAULT_MODE = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO


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

