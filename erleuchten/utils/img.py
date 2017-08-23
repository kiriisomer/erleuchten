# coding:utf-8

import guestfs
from erleuchten.utils import conf
from erleuchten.utils.error import ErleuchtenException
from erleuchten.utils.error import Errno


def launch_vm(disk):
    gfs = guestfs.GuestFS(python_return_dict=True)
    gfs.add_drive_opts(disk, readonly=0)
    gfs.launch()
    l = gfs.list_filesystems()
    for key, value in l.items():
        if value == 'swap':
            sw = key
    del l[sw]
    li = list(l)
    for item in li:
        gfs.mount(item, "/")
    return gfs


def ls(disk, dir):
    gfs = launch_vm(disk)
    result = gfs.ls(dir)
    re = '\n'.join(result)
    return re


def new(disk, file):
    gfs = launch_vm(disk)
    gfs.touch(file)


def remove(disk, file):
    gfs = launch_vm(disk)
    gfs.rm(file)


def write(disk, file, content):
    gfs = launch_vm(disk)
    gfs.write(file, content)


def write_append(disk, file, content):
    gfs = launch_vm(disk)
    gfs.write_append(file, content)


def find(disk, dir):
    gfs = launch_vm(disk)
    return gfs.find(dir)


def cat(disk, file):
    gfs = launch_vm(disk)
    return gfs.cat(file)


def download(disk, source, target):
    """copies remote files or directories recursively out of the disk image"""
    gfs = launch_vm(disk)
    try:
        gfs.download(source, target)
    except IOError:
        raise ErleuchtenException(errno=Errno.ERRNO_NO_SUCH_FILE)


def upload(disk, source, target):
    """copies local files or directories
    recursively into the disk image(overwrite)"""
    gfs = launch_vm(disk)
    try:
        gfs.upload(source, target)
    except:
        raise ErleuchtenException(errno=Errno.ERRNO_NO_SUCH_FILE)


def modify_ifcfg(disk, srcifcfg, ip,
                 mask='255.255.255.0', gateway='192.168.16.254',
                 dns='114.114.114.114', flag=0):
    """modify vm network configuration"""
    # 利用flag参数将没必要的参数注释掉

    # a,b,c,d为设置的标志，当原网卡文件中有ip,mask,gateway或dns时，则在相应的行
    # 进行修改，若原网卡文件没有相应的内容，则在文件末尾添加相应内容
    a, b, c, d = 0, 0, 0, 0
    # tmppath为从源虚拟机download下来的网卡文件，newifcfg为对该网卡文件修改之后
    # 生成的新的网卡文件
    tmppath = conf.get('IFCFG_TEMP')
    newifcfg = conf.get('NEWIFCFG')
    download(disk, srcifcfg, tmppath)
    ipaddr = ip
    netmask = mask
    gatewway = gateway
    ddns = dns
    # fd1为从源虚拟机下载下来的原始网卡文件
    fd1 = open(tmppath, 'r+')
    # fd2为将原始网卡文件进行修改之后的新的网卡文件
    fd2 = open(newifcfg, 'w')
    # for循环对网卡文件中的相关内容进行修改
    for line in fd1:
        if line.strip().startswith("BOOTPROTO"):
            fd2.write("BOOTPROTO=static\n")
        elif line.strip().startswith("ONBOOT"):
            fd2.write("ONBOOT=yes\n")
        elif line.strip().startswith("IPADDR"):
            a = 1
            fd2.write("IPADDR=%s\n" % ipaddr)
        elif line.strip().startswith("NETMASK"):
            b = 1
            fd2.write("NETMASK=%s\n" % netmask)
        elif line.strip().startswith("GATEWAY"):
            c = 1
            if flag == 0:
                fd2.write("GATEWAY=%s\n" % gatewway)
            if flag == 1:
                fd2.write("# GATEWAY=%s\n" % gatewway)
        elif line.strip().startswith("DNS"):
            d = 1
            if flag == 0:
                fd2.write("DNS1=%s\n" % ddns)
            if flag == 1:
                fd2.write("# DNS1=%s\n" % ddns)
        else:
            fd2.write(line)
    fd1.close()
    # 如果网卡文件不存在相应信息，则直接在文件末尾进行添加
    if a != 1:
        fd2.seek(0, 2)
        fd2.write("IPADDR=%s\n" % ipaddr)
    if b != 1:
        fd2.seek(0, 2)
        fd2.write("NETMASK=%s\n" % netmask)
    if c != 1:
        fd2.seek(0, 2)
        fd2.write("GATEWAY=%s\n" % gatewway)
    if d != 1:
        fd2.seek(0, 2)
        fd2.write("DNS1=%s\n" % ddns)
    fd2.close()
    # 将新的网卡文件上传并覆盖至克隆的虚拟机
    upload(disk, newifcfg, srcifcfg)


def shutdown_vm(disk):
    """umount all filesystems, shutdown vm, close guestfs"""
    gfs = launch_vm(disk)
    gfs.umount_all()
    gfs.shutdown()
    gfs.close()
