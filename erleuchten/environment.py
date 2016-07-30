# coding:utf-8

# prepare testing environment(vm, software, yeesan, etc.)
import os
from uuid import uuid4

import StringIO
import shutil
import libvirt

from erleuchten.util import conf
from erleuchten.util.error import ErleuchtenException
from erleuchten.util.error import Errno
from erleuchten.util.xml import VMXML, EnvironmentConf
from erleuchten.util.util import copy_file

HYPERVISOR_URI = "qemu:///system"
DISK_XML = ("<disk type='file' device='disk'>"
            "<driver name='qemu' type='{format}'/>"
            "<source file='{source}'/>"
            "<target dev='{target}' bus='virtio'/>"
            "</disk>")


VMTEMPLATE_STATUS_UNKNOWN = 'unknown'
VMTEMPLATE_STATUS_NORMAL = 'normal'
VMTEMPLATE_STATUS_BAD = 'bad'

ENVVM_STATUS_UNKNOWN = 'unknown'    # 未知，未初始化
ENVVM_STATUS_STOP = 'stop'          # 初始化完毕，正常停止状态，
ENVVM_STATUS_RUNNING = 'runnning'   # 初始化完毕，运行状态，


# ##############################################################################
#
# ##############################################################################
def list_domains(status):
    domains = []
    if status in ['all', 'running']:
        domains += _list_active_domains()
    if status in ['all', 'stopped']:
        domains += _list_inactive_domains()
    return domains


def _list_active_domains():
    conn = libvirt.open(HYPERVISOR_URI)
    domains = []
    for id_ in conn.listDomainsID():
        domains.append(conn.lookupByID(id_).name())
    return domains


def _list_inactive_domains():
    conn = libvirt.open(HYPERVISOR_URI)
    return conn.listDefinedDomains()


def poweron_domain_by_name(domain_name):
    try:
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(domain_name)
        if dom.create() == 0:
            print("domain <name: {0}> start".format(domain_name))
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


def undefine_domain_by_name(domain_name):
    try:
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(domain_name)
        if dom.undefine() == 0:
            print("domain <name: {0}> undefine".format(domain_name))
        else:
            print("domain <name: {0}> undefine failed".format(domain_name))
    except libvirt.libvirtError, e:
        print("shutdown failed")
        print(e)
        return


def list_domain_disk(domain_name):
    conn = libvirt.open(HYPERVISOR_URI)
    dom = conn.lookupByName(domain_name)
    xmldata = dom.XMLDesc(0)
    xml_obj = VMXML(StringIO.StringIO(xmldata))
    return xml_obj.get_all_disk_device()


def attach_disk(domain_name, src, tgt, fmt):
    conn = libvirt.open(HYPERVISOR_URI)
    dom = conn.lookupByName(domain_name)
    disk_xml = DISK_XML.format(source=src, target=tgt, format=fmt)
    dom.attachDevice(disk_xml)


def detach_disk(domain_name, tgt):
    conn = libvirt.open(HYPERVISOR_URI)
    dom = conn.lookupByName(domain_name)

    xmldata = dom.XMLDesc(0)
    xml_obj = VMXML(StringIO.StringIO(xmldata))
    (_, src, fmt) = xml_obj.get_disk_device_info_by_dev(tgt)

    disk_xml = DISK_XML.format(source=src, target=tgt, format=fmt)
    dom.detachDevice(disk_xml)


def clone_vm_by_domain_name(dom_name, new_dom_name):
    if dom_name == new_dom_name:
        raise ErleuchtenException(Errno.ERRNO_XML_DONAMIN_NAME_CONFLICT)
    conn = libvirt.open(HYPERVISOR_URI)
    dom = conn.lookupByName(dom_name)

    # 获取原有的虚拟机xml
    xmldata = dom.XMLDesc(0)
    xml_obj = VMXML(StringIO.StringIO(xmldata))

    # 修改xml属性
    xml_obj.modify_vm_name(new_dom_name)
    xml_obj.modify_vm_uuid(str(uuid4()))

    dev_cnt = 0
    for dev in xml_obj.get_all_disk_device():
        orig_path, orig_name = os.path.split(dev[1])
        l = orig_name.partition('.')

        new_name = "".join(["%s_%04d" % (new_dom_name, dev_cnt), l[1], l[2]])
        new_disk_path = os.path.join(orig_path, new_name)
        xml_obj.modify_disk_file_path(dev[0], new_disk_path)
        copy_file(dev[1], new_disk_path)
        dev_cnt += 1

    xml_obj.randomize_interface_mac()

    # 获取新的xml文件，定义虚拟机
    conn.defineXML(xml_obj.get_xml_str())


# ##############################################################################
#
# ##############################################################################
def create_env(name):
    if os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(name))
        return


# ##############################################################################
#
# ##############################################################################
# class VM(object):
#     """single VM"""

#     def __init__(self):
#         self.name = ""
#         self.env_name = ""
#         self.order = -1
#         self.status = ENVVM_STATUS_UNKNOWN
#         self.ip = ""
#         self.mask = ""
#         self.gateway = ""
#         self.dns = ""
#         self.ssh_user = "root"
#         self.ssh_user_pswd = "111111"


class VM(object):
    """VM template"""

    def __init__(self):
        self.name = ""
        self.xml_obj = None
        self.status = ENVVM_STATUS_UNKNOWN
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
        self.vm_info = []   # [{}, {}]
        self.conf_obj = None

    def initial(self, name, ):
        """初始化一个新的对象"""
        self.name = name

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        # 返回文件路径，使用sh执行
        self.name = name
        conf_obj = ScriptConf(os.path.join(conf.PATH_ENVIRONMENT, self.name,
                                           "%s.conf" % self.name), self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj.xml_root_obj is None and conf_obj.get_name() is None:
            return
            # raise error.ScriptError(error.ERRNO_SCRIPT_OPENCONF_ERROR)
        conf_dict = conf_obj.load_config()
        self.script_name = conf_dict["script_name"]
        self.pid = int(conf_dict["pid"])
        self.exceed_time = int(conf_dict["exceed_time"])
        self.status = conf_dict["status"]
    def add_domain_desc(self, name, src_name, addr, mask, gateway, dns,
                        ssh_user, ssh_password):
        desc_dict = {
            "name": "",
            "src_name": "",
            "addr": "",
            "mask": "",
            "gateway": "",
            "dns": "",
            "ssh_user": "",
            "ssh_password": ""
        }




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
