# coding:utf-8

# prepare testing environment(vm, software, yeesan, etc.)
import os
from uuid import uuid4

import StringIO
import shutil
import libvirt

from erleuchten.util import conf, remote
from erleuchten.util.error import ErleuchtenException
from erleuchten.util.error import Errno
from erleuchten.util.xml import VMXML, EnvConf
from erleuchten.util.util import create_dir, copy_file

HYPERVISOR_URI = "qemu:///system"
DISK_XML = ("<disk type='file' device='disk'>"
            "<driver name='qemu' type='{format}'/>"
            "<source file='{source}'/>"
            "<target dev='{target}' bus='virtio'/>"
            "</disk>")


ENV_STATUS_UNKNOWN = 'unknown'
ENV_STATUS_NORMAL = 'normal'
ENV_STATUS_BAD = 'bad'

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

    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.initial(name)
    env_obj.save_conf()


def remove_env(name, force=False):
    shutil.rmtree(os.path.join(conf.PATH_ENVIRONMENT, name))


def env_add_domain(name, vm_info_dict):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.add_domain_desc(vm_info_dict.get("name", ""),
                            vm_info_dict.get("src_name", ""),
                            vm_info_dict.get("if_name", ""),
                            vm_info_dict.get("addr", ""),
                            vm_info_dict.get("mask", ""),
                            vm_info_dict.get("gateway", ""),
                            vm_info_dict.get("dns", ""),
                            vm_info_dict.get("ssh_user", ""),
                            vm_info_dict.get("ssh_password", ""))
    env_obj.save_conf()


def env_modify_domain(name, vm_info_dict):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.modify_domain_desc(vm_info_dict.get("name", ""),
                               vm_info_dict.get("src_name", ""),
                               vm_info_dict.get("if_name", ""),
                               vm_info_dict.get("addr", ""),
                               vm_info_dict.get("mask", ""),
                               vm_info_dict.get("gateway", ""),
                               vm_info_dict.get("dns", ""),
                               vm_info_dict.get("ssh_user", ""),
                               vm_info_dict.get("ssh_password", ""))
    env_obj.save_conf()


def env_remove_domain(name, vm_name):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.remove_domain_desc(vm_name)
    env_obj.save_conf()


def env_initial(name):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.initial_all_vm()


def env_start(name):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.start_all_vm()


def env_shutdown(name):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.shutdown_all_vm()


def env_get_vm_list(name):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    return env_obj.get_vm_list()


def env_get_vm_info(name, vm_name):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return {}

    env_obj = Environment()
    env_obj.load_conf(name)
    return env_obj.get_vm_info(vm_name)


def list_env():
    if not os.path.exists(conf.PATH_ENVIRONMENT):
        create_dir(conf.PATH_ENVIRONMENT)
    result = []
    for i in os.listdir(conf.PATH_ENVIRONMENT):
        try:
            if os.path.isfile(os.path.join(conf.PATH_ENVIRONMENT, i,
                                           "%s.conf" % i)):
                result.append(i)
        except OSError:
            continue

    return result


def env_ssh_cmd(name, vm_name, cmd):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    return env_obj.remote_cmd(vm_name, cmd)


def env_ssh_put(name, vm_name, src, dst):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    return env_obj.remote_put(vm_name, src, dst)


def env_ssh_get(name, vm_name, src, dst):
    if not os.path.exists(os.path.join(conf.PATH_ENVIRONMENT, name,
                                       "%s.conf" % name)):
        print("environment not found")
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    return env_obj.remote_get(vm_name, src, dst)


# ##############################################################################
#
# ##############################################################################
class EnvVM(object):
    """虚拟机描述信息"""

    def __init__(self, desc_dict):
        self.name = desc_dict["name"]
        self.env_name = desc_dict["env_name"]
        self.ip = desc_dict["ip"]
        self.mask = desc_dict["mask"]
        self.gateway = desc_dict["gateway"]
        self.dns = desc_dict["dns"]
        self.ssh_user = desc_dict["ssh_user"]
        self.ssh_password = desc_dict["ssh_password"]

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(key)

    def __setitem__(self, key, val):
        if hasattr(self, key):
            return setattr(self, key, val)
        else:
            raise KeyError('object EnvVM is not a Dict, '
                           'cannot set item "%s"' % key)

    def ssh_process_cmd(self, cmd):
        return remote.fabric_command(self.ip, self.ssh_user,
                                     self.ssh_password, cmd)

    def ssh_put(self, local_src, remote_dst):
        return remote.fabric_command(self.ip, self.ssh_user,
                                     self.ssh_password, local_src, remote_dst)

    def ssh_get(self, local_src, remote_dst):
        return remote.fabric_command(self.ip, self.ssh_user,
                                     self.ssh_password, local_src, remote_dst)


# class VM(object):
#     """VM template"""

#     def __init__(self):
#         self.name = ""
#         self.xml_obj = None
#         self.status = ENVVM_STATUS_UNKNOWN
#         # self.device_path_dict = {}

#     def initial(self, name):
#         """init class by vm_template's name"""
#         self.name = name
#         xml_path = os.path.join(conf.PATH_VM_TEMPLATE, self.name,
#                                 "%s.xml" % self.name)
#         self.xml_obj = VMXML(xml_path)

#         # self.device_path_dict = {}

#     def cerate(self):
#         """add a template"""
#         self._create_from_local_xml()

#     def remove(self):
#         """remove a template from disk"""
#         # remove xml file and related disk img
#         for i in self.device_path_dict.values():
#             os.unlink(i)
#         os.unlink(self.xml_obj.xml_path)

#         # reset param
#         self.name = ""
#         self.status = ENVVM_STATUS_UNKNOWN
#         self.xml_obj = None
#         # self.device_path_dict = {}

#     def _create_from_local_xml(self, name, xml_path, move_dev_files=False):
#         """从XML描述文件创建一个模板。
#         将XML文件复制到自己的目录，指定了move_dev_files的话，连磁盘文件也
#         一并复制进来"""
#         self.name = name
#         new_xml_path = os.path.join(conf.PATH_VM_TEMPLATE, self.name,
#                                     "%s.xml" % self.name)
#         # 复制xml文件到目录中。
#         shutil.copy(xml_path, new_xml_path)
#         # if move_dev_files:
#         #     for i in self.xml.get_device_path_list():

#     def copy(self, src_obj):
#         """copy and create a new VMTemplate"""


class Environment(object):
    """an environment is a series of virtual machines."""

    def __init__(self):
        self.name = ""
        self.vm_info_list = []   # [{}, {}]
        self.status = ENV_STATUS_UNKNOWN
        self.conf_obj = None

    def initial(self, name):
        """初始化一个新的对象"""
        self.name = name

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        self.name = name
        conf_obj = EnvConf(os.path.join(conf.PATH_ENVIRONMENT, self.name,
                                        "%s.conf" % self.name), self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj.xml_root_obj is None and conf_obj.get_name() is None:
            return
            # raise ErleuchtenException(Errno.ERRNO_OPENCONF_ERROR)
        conf_dict = conf_obj.load_config()
        self.status = conf_dict["status"]
        self.vm_info_list = conf_dict["vm_info_list"]

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        conf_dict = {
            "name": self.name,
            "status": self.status,
            "vm_info_list": self.vm_info_list
        }
        self.conf_obj.save_config(conf_dict)

    def add_domain_desc(self, name, src_name, if_name, addr, mask, gateway,
                        dns, ssh_user, ssh_password):
        """添加一个虚拟机描述"""
        # 检查是否已经添加过
        if name in [x['name'] for x in self.vm_info_list]:
            return

        desc_dict = {
            "name": name,
            "src_name": src_name,
            "if_name": if_name,
            "addr": addr,
            "mask": mask,
            "gateway": gateway,
            "dns": dns,
            "ssh_user": ssh_user,
            "ssh_password": ssh_password
        }
        self.vm_info_list.append(desc_dict)

    def modify_domain_desc(self, name, src_name, if_name, addr, mask, gateway,
                           dns, ssh_user, ssh_password):
        """添加一个虚拟机描述"""
        desc_dict = {}
        if name is not None:
            desc_dict["name"] = name
        if src_name is not None:
            desc_dict["src_name"] = src_name
        if if_name is not None:
            desc_dict["if_name"] = if_name
        if addr is not None:
            desc_dict["addr"] = addr
        if mask is not None:
            desc_dict["mask"] = mask
        if gateway is not None:
            desc_dict["gateway"] = gateway
        if dns is not None:
            desc_dict["dns"] = dns
        if ssh_user is not None:
            desc_dict["ssh_user"] = ssh_user
        if ssh_password is not None:
            desc_dict["ssh_password"] = ssh_password

        for i in range(len(self.vm_info_list)):
            if self.vm_info_list[i]["name"] == name:
                self.vm_info_list[i].update(desc_dict)
                return
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def initial_all_vm(self):
        """initial env VMs"""
        for i in self.vm_info_list:
            clone_vm_by_domain_name(i["src_name"], i["name"])

    def start_all_vm(self):
        """poweron env VMs"""
        for i in self.vm_info_list:
            try:
                poweron_domain_by_name(i["name"])
            except libvirt.libvirtError, e:
                if e.err[0] == libvirt.VIR_ERR_OPERATION_INVALID:
                    # domain is already running
                    continue
                raise

    def shutdown_all_vm(self):
        """shutdown env VMs"""
        for i in self.vm_info_list:
            try:
                destroy_domain_by_name(i["name"])
            except libvirt.libvirtError, e:
                if e.err[0] == libvirt.VIR_ERR_OPERATION_INVALID:
                    # domain is not running
                    continue
                raise

    def remove_domain_desc(self, vm_name):
        """remove VM from environment"""
        for i in range(len(self.vm_info_list)):
            if self.vm_info_list[i]["name"] == vm_name:
                del self.vm_info_list[i]
                break

    def get_vm_list(self):
        return [x['name'] for x in self.vm_info_list]

    def get_vm_info(self, vm_name):
        for i in self.vm_info_list:
            if i["name"] == vm_name:
                return i
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def remote_cmd(self, vm_name, cmd):
        for i in self.vm_info_list:
            if i["name"] == vm_name:
                return remote.fabric_command(i["addr"], i["ssh_user"],
                                             i["ssh_password"], cmd)
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def remote_put(self, vm_name, local_src, remote_dst):
        for i in self.vm_info_list:
            if i["name"] == vm_name:
                return remote.fabric_put(i["addr"], i["ssh_user"],
                                         i["ssh_password"],  local_src,
                                         remote_dst)
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def remote_get(self, vm_name, remote_src, local_dst):
        for i in self.vm_info_list:
            if i["name"] == vm_name:
                return remote.fabric_get(i["addr"], i["ssh_user"],
                                         i["ssh_password"], remote_src,
                                         local_dst)
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)
