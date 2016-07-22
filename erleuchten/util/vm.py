# coding:utf-8

# vm function utils

import libvirt


def get_conn(addr="qemu:///system"):
    conn = libvirt.open(addr)
    return conn


def list_domains(conn)
