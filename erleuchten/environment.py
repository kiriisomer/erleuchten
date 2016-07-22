# coding:utf-8

# prepare testing environment(vm, software, yeesan, etc.)
import os

import shutil
import libvirt
from erleuchten.util import conf
from erleuchten.util import VMXML

HYPERVISOR_URI = "qemu:///system"
VMTEMPLATE_STATUS_UNKNOWN = 'unknown'
VMTEMPLATE_STATUS_NORMAL = 'normal'
VMTEMPLATE_STATUS_BAD = 'bad'

ENVVM_STATUS_UNKNOWN = 'unknown'    # 未知，未初始化
ENVVM_STATUS_STOP = 'stop'          # 初始化完毕，正常停止状态，
ENVVM_STATUS_RUNNING = 'runnning'   # 初始化完毕，运行状态，


def list_domains(status):
    domains = []
    if status in ['all', 'running']:
        domains += _list_active_domains()
    if status in ['all', 'stopped']:
        domains += _list_inactive_domains()
    print('\n'.join(domains))


def _list_active_domains():
    conn = libvirt.open(HYPERVISOR_URI)
    domains = []
    for id_ in conn.listDomainsID():
        domains.append(conn.lookupByID(id_).name())
    return domains


def _list_inactive_domains():
    conn = libvirt.open(HYPERVISOR_URI)
    domains = []
    for id_ in conn.listDefinedDomains():
        domains.append(conn.lookupByID(id_).name())
    return domains


def poweron_domain_by_id(domain_id):
    try:
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByID(domain_id)
        if dom.create() == 0:
            print("domain <id: {0}> started".format(domain_id))
        else:
            print("domain <id: {0}> start failed".format(domain_id))
    except libvirt.libvirtError, e:
        print("poweron failed")
        print(e)
        return


def poweron_domain_by_name(domain_name):
    try:
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(domain_name)
        if dom.create() == 0:
            print("domain <name: {0}> started".format(domain_name))
        else:
            print("domain <name: {0}> start failed".format(domain_name))
    except libvirt.libvirtError, e:
        print("poweron failed")
        print(e)
        return


def poweroff_domain_by_name(domain_name):
    try:
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(domain_name)
        if dom.shutdown() == 0:
            print("domain <name: {0}> shutdown".format(domain_name))
        else:
            print("domain <name: {0}> shutdown failed".format(domain_name))
    except libvirt.libvirtError, e:
        print("shutdown failed")
        print(e)
        return


def destroy_domain_by_name(domain_name):
    try:
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(domain_name)
        if dom.destroy() == 0:
            print("domain <name: {0}> shutdown".format(domain_name))
        else:
            print("domain <name: {0}> shutdown failed".format(domain_name))
    except libvirt.libvirtError, e:
        print("shutdown failed")
        print(e)
        return


def list_domain_disk(status):


class VM(object):
    """single VM"""

    def __init__(self):
        self.name = ""
        self.env_name = ""
        self.order = -1
        self.status = ENVVM_STATUS_UNKNOWN
        self.ip = ""
        self.ssh_user = "root"
        self.ssh_user_pswd = "111111"


class VMTemplate(object):
    """VM template"""

    def __init__(self):
        self.name = ""
        self.xml_obj = None
        self.status = VMTEMPLATE_STATUS_UNKNOWN
        # self.device_path_dict = {}

    def initial(self, name):
        """init class by vm_template's name"""
        self.name = name
        xml_path = os.path.join(conf.PATH_VM_TEMPLATE, self.name,
                                "%s.xml" % self.name)
        self.xml_obj = VMXML(xml_path)

        # self.device_path_dict = {}

    def cerate(self):
        """add a template"""
        self._create_from_local_xml()

    def remove(self):
        """remove a template from disk"""
        # remove xml file and related disk img
        for i in self.device_path_dict.values():
            os.unlink(i)
        os.unlink(self.xml_obj.xml_path)

        # reset param
        self.name = ""
        self.status = VMTEMPLATE_STATUS_UNKNOWN
        self.xml_obj = None
        # self.device_path_dict = {}

    def _create_from_local_xml(self, name, xml_path, move_dev_files=False):
        """从XML描述文件创建一个模板。
        将XML文件复制到自己的目录，指定了move_dev_files的话，连磁盘文件也
        一并复制进来"""
        self.name = name
        new_xml_path = os.path.join(conf.PATH_VM_TEMPLATE, self.name,
                                    "%s.xml" % self.name)
        # 复制xml文件到目录中。
        shutil.copy(xml_path, new_xml_path)
        # if move_dev_files:
        #     for i in self.xml.get_device_path_list():

    def copy(self, src_obj):
        """copy and create a new VMTemplate"""


class Environment(object):
    """an environment is a series of virtual machines."""

    def __init__(self):
        self.name = ""
        self.vm_info = {}   # {vm_name: vm_class}

    def create(self):
        """create an environment"""

    def initial_VM(self):
        """create an env, initial VMs"""

    def launch(self):
        """poweron env's VMs"""

    def shutdown(self):
        """shutdown env's VMs"""

    def remove_VM(self):
        """remove VM from disk and environment"""
