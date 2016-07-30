# coding:utf-8

import os
import guestfs


def get_gfs_vm(diskpath):
    gfs = guestfs.GuestFS(python_return_dict=True)
    gfs.add_drive_opts(diskpath, readonly=0)
    gfs.launch()
    l = gfs.list_filesystems()
    li = list(l)
    lis = li[1:]
    for item in lis:
        gfs.mount(item, "/")
    return gfs


def ls(diskpath, directory):
    gfs = get_gfs_vm(diskpath)
    print gfs.ls(directory)


def new(diskpath, filepath):
    gfs = get_gfs_vm(diskpath)
    gfs.touch(filepath)


def remove(diskpath, filepath):
    gfs = get_gfs_vm(diskpath)
    gfs.rm(filepath)


def write(diskpath, filepath, content):
    gfs = get_gfs_vm(diskpath)
    gfs.write(filepath, content)


def write_append(diskpath, filepath, content):
    gfs = get_gfs_vm(diskpath)
    gfs.write_append(filepath, content)


def find(diskpath, directory):
    gfs = get_gfs_vm(diskpath)
    return gfs.find(directory)


def cat(diskpath, filepath):
    gfs = get_gfs_vm(diskpath)
    return gfs.cat(filepath)


def download(diskpath, sourcepath, targetpath):
    """copies remote files or directories recursively out of the disk image"""
    gfs = get_gfs_vm(diskpath)
    if gfs.is_file(sourcepath):
        print "%s exists" % sourcepath
        gfs.download(sourcepath, targetpath)
        print "%s download successful" % sourcepath
    else:
        print "%s doesn\'t exists" % sourcepath


def upload(diskpath, sourcepath, targetpath):
    """copies local files or directories
    recursively into the disk image(overwrite)"""
    gfs = get_gfs_vm(diskpath)
    if os.path.isfile(sourcepath):
        print "%s exists" % sourcepath
        gfs.upload(sourcepath, targetpath)
        print "%s upload successful" % sourcepath
    else:
        print "%s doesn't exists" % sourcepath


def modifyifcfg(diskpath, oldifcfg, tmppath, newifcfg, ip):
    """modify vm network configuration"""
    t = 0, 0, 0, 0
    a, b, c, d = t
    download(diskpath, oldifcfg, tmppath)
    ipaddr = ip
    fd1 = open(tmppath, 'r+')
    fd2 = open(newifcfg, 'w')
    for eachLine in fd1:
        if eachLine.strip().startswith("BOOTPROTO"):
            fd2.write("BOOTPROTO=static\n")
        elif eachLine.strip().startswith("ONBOOT"):
            fd2.write("ONBOOT=yes\n")
        elif eachLine.strip().startswith("IPADDR"):
            a = 1
            fd2.write("IPADDR=%s\n" % ipaddr)
        elif eachLine.strip().startswith("NETMASK"):
            b = 1
            fd2.write("NETMASK=255.255.255.0\n")
        elif eachLine.strip().startswith("GATEWAY"):
            c = 1
            fd2.write("GATEWAY=192.168.16.254\n")
        elif eachLine.strip().startswith("DNS"):
            d = 1
            fd2.write("DNS=114.114.114.114\n")
        else:
            fd2.write(eachLine)
    fd1.close()
    if a != 1:
        fd2.seek(0, 2)
        fd2.write("IPADDR=%s\n" % ipaddr)
    if b != 1:
        fd2.seek(0, 2)
        fd2.write("NETMASK=255.255.255.0\n")
    if c != 1:
        fd2.seek(0, 2)
        fd2.write("GATEWAY=192.168.16.254\n")
    if d != 1:
        fd2.seek(0, 2)
        fd2.write("DNS=114.114.114.114\n")
    fd2.close()
    upload(diskpath, newifcfg, oldifcfg)
    print "network configuration modify successful"


def shutdown_vm(diskpath):
    """umount all filesystems, shutdown vm, close guestfs"""
    gfs = get_gfs_vm(diskpath)
    gfs.umount_all()
    gfs.shutdown()
    gfs.close()




