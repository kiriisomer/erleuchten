# coding:utf-8

# prepare testing environment(vm, software, etc.)
from uuid import uuid4

import StringIO
import libvirt
import subprocess
import os

from erleuchten.utils.error import ErleuchtenException
from erleuchten.utils.error import Errno
from erleuchten.utils.xml import VMXML
from erleuchten.utils.img import modify_ifcfg
from erleuchten.utils.util import copy_file

HYPERVISOR_URI = "qemu:///system"
DISK_XML = ("<disk type='file' device='disk'>"
            "<driver name='qemu' type='{format}'/>"
            "<source file='{source}'/>"
            "<target dev='{target}' bus='virtio'/>"
            "</disk>")


VM_STATUS_UNKNOWN = 'unknown'    # 未知，未初始化
VM_STATUS_STOP = 'stop'          # 初始化完毕，正常停止状态，
VM_STATUS_RUNNING = 'runnning'   # 初始化完毕，运行状态，


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
# ##############################################################################
#
# ##############################################################################


class VM(object):
    def __init__(self, name):
        self.vm_name = name

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise KeyError(key)

    def __setitem__(self, key, val):
        if hasattr(self, key):
            return setattr(self, key, val)
        else:
            raise KeyError('object VM is not a Dict, '
                           'cannot set item "%s"' % key)

    def getstatus(self):
        conn = libvirt.open(HYPERVISOR_URI)
        doms = conn.listAllDomains()
        for dom in doms:
            if dom.name() == self.vm_name:
                if dom.state()[0] == 1:
                    return VM_STATUS_RUNNING
                if dom.state()[0] == 5:
                    return VM_STATUS_STOP

        return VM_STATUS_UNKNOWN

    def clone(self, desc_dict):
        """
        clone a vm based on an existed vm using another description dictionary,
        this dictionary should at least include:
        "vm_src_name" name of the source vm
        "manage_ifcfg_source" path of the config file of the interface (eth0,
        usually)
        "manage_if_name" name of this interface for further connecting and
        disconnecting this interface
        "manage_mask" network mask
        "manage_dns" network dns
        "manage_addr" IP address
        "manage_gateway" network gateway
        "storage_ifcfg_source"
        "storage_if_name"
        "storage_mask"
        "storage_addr"
        "storage_gateway"
        "ssh_user" user name for further login through ssh
        "ssh_password" password for further login through ssh
        """

        if self.getstatus() != VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_ALREADY_CLONED)

        if self.vm_name == desc_dict["vm_src_name"]:
            raise ErleuchtenException(Errno.ERRNO_VM_NAME_CONFLICT)

        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(desc_dict["vm_src_name"])

        if dom.state()[0] != 5:
            raise ErleuchtenException(Errno.ERRNO_SOURCE_VM_RUNNING)

        # 获取原有的虚拟机xml
        xmldata = dom.XMLDesc(0)
        xml_obj = VMXML(StringIO.StringIO(xmldata))

        # 修改xml属性
        xml_obj.modify_vm_name(self.vm_name)
        xml_obj.modify_vm_uuid(str(uuid4()))

        names = [desc_dict["manage_if_name"], desc_dict["storage_if_name"]]
        xml_obj.modify_interfaces_name(names)

        dev_cnt = 0
        for dev in xml_obj.get_all_disk_device():
            orig_path, orig_name = os.path.split(dev[1])
            l = orig_name.partition('.')

            new_name = "".join(["%s_%04d" % (self.vm_name, dev_cnt),
                                l[1], l[2]])
            new_disk_path = os.path.join(orig_path, new_name)
            xml_obj.modify_disk_file_path(dev[0], new_disk_path)
            copy_file(dev[1], new_disk_path)
            dev_cnt += 1
            if dev[0] == 'hda':
                modify_ifcfg(new_disk_path, desc_dict["manage_ifcfg_source"],
                             desc_dict["manage_addr"],
                             desc_dict["manage_mask"],
                             desc_dict["manage_gateway"],
                             desc_dict["manage_dns"])
                modify_ifcfg(new_disk_path, desc_dict["storage_ifcfg_source"],
                             desc_dict["storage_addr"],
                             desc_dict["storage_mask"],
                             desc_dict["manage_gateway"],
                             desc_dict["manage_dns"], 1)

        xml_obj.randomize_interface_mac()

        # 获取新的xml文件，定义虚拟机
        conn.defineXML(xml_obj.get_xml_str())

        return

    def poweron(self):
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        if self.getstatus() == VM_STATUS_RUNNING:
            return
        try:
            conn = libvirt.open(HYPERVISOR_URI)
            dom = conn.lookupByName(self.vm_name)
            dom.create()
        except libvirt.libvirtError:
            raise

        return

    def poweroff(self):
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        if self.getstatus() == VM_STATUS_STOP:
            return
        try:
            conn = libvirt.open(HYPERVISOR_URI)
            dom = conn.lookupByName(self.vm_name)
            dom.shutdown()
        except libvirt.libvirtError:
            raise

        return

    def undefine_domain(self):
        """
        Undefine a domain. If the domain is running, it's converted to
        transient domain, without stopping it. If the domain is inactive,
        the domain configuration is removed.
        """
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        try:
            conn = libvirt.open(HYPERVISOR_URI)
            dom = conn.lookupByName(self.vm_name)
            dom.undefine()
        except libvirt.libvirtError:
            raise

        return

    def destroy(self):
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        if self.getstatus() == VM_STATUS_STOP:
            return
        try:
            conn = libvirt.open(HYPERVISOR_URI)
            dom = conn.lookupByName(self.vm_name)
            dom.destroy()
        except libvirt.libvirtError:
            raise

        return

    def list_disks(self):
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(self.vm_name)

        xmldata = dom.XMLDesc(0)
        xml_obj = VMXML(StringIO.StringIO(xmldata))

        return xml_obj.get_all_disk_device()

    def attach_disk(self, src, tgt, fmt):
        """
        attach a disk to the vm, three parameters are needed at least
        src specifies where the disk image is
        tgt specifies the target device as which the disk is going to be shown
        fmt specifies the format of the disk image
        """
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(self.vm_name)

        disk_xml = DISK_XML.format(source=src, target=tgt, format=fmt)
        dom.attachDevice(disk_xml)

        return

    def detach_disk(self, tgt):
        """
        detach a disk from the vm, one parameter is needed at least
        tgt specifies the disk name on the vm that you want to detach
        """
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(self.vm_name)

        xmldata = dom.XMLDesc(0)
        xml_obj = VMXML(StringIO.StringIO(xmldata))
        (_, src, fmt) = xml_obj.get_disk_device_info_by_dev(tgt)

        disk_xml = DISK_XML.format(source=src, target=tgt, format=fmt)
        dom.detachDevice(disk_xml)

        return

    def list_interfaces(self):
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        if self.getstatus() != VM_STATUS_RUNNING:
            raise ErleuchtenException(Errno.ERRNO_VM_NOT_RUNNING)

        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(self.vm_name)

        xmldata = dom.XMLDesc(0)
        xml_obj = VMXML(StringIO.StringIO(xmldata))

        return xml_obj.get_all_interfaces()

    def connect_interface(self, interface):
        """
        restore the connection of a interface specified by the parameter "inte-
        rface, you should always use VM.list_interfaces() before this"
        """
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        if self.getstatus() != VM_STATUS_RUNNING:
            raise ErleuchtenException(Errno.ERRNO_VM_NOT_RUNNING)

        interface_not_exist = True
        if_list = self.list_interfaces()
        for iface in if_list:
            if interface == iface[3]:
                interface_not_exist = False
                break
        if interface_not_exist:
            raise ErleuchtenException(Errno.ERRNO_VM_NO_SUCH_INTERFACE)

        # connect to the hypervisor
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(self.vm_name)

        # get the bridge on which the interface is attached
        xmldata = dom.XMLDesc(0)
        xml_obj = VMXML(StringIO.StringIO(xmldata))
        bridge = xml_obj.get_bridge(interface)

        # add the interface to the bridge through "brctl addif"
        p = subprocess.Popen(['brctl', 'addif', bridge, interface])
        p.wait()
        temp = p.returncode
        if temp != 0:
            print("Add interface <name: {0}> failed".format(interface))

        return

    def disconnect_interface(self, interface):
        """
        cut off the connection of a interface specified by the parameter "inte-
        rface, you should always use VM.list_interfaces() before this"
        """
        if self.getstatus() == VM_STATUS_UNKNOWN:
            raise ErleuchtenException(Errno.ERRNO_VM_STATUS_UNKNOWN)

        if self.getstatus() != VM_STATUS_RUNNING:
            raise ErleuchtenException(Errno.ERRNO_VM_NOT_RUNNING)

        interface_not_exist = True
        if_list = self.list_interfaces()
        for iface in if_list:
            if interface == iface[3]:
                interface_not_exist = False
                break
        if interface_not_exist:
            raise ErleuchtenException(Errno.ERRNO_VM_NO_SUCH_INTERFACE)
        # connect to the hypervisor
        conn = libvirt.open(HYPERVISOR_URI)
        dom = conn.lookupByName(self.vm_name)

        # get the bridge on which the interface is attached
        xmldata = dom.XMLDesc(0)
        xml_obj = VMXML(StringIO.StringIO(xmldata))
        bridge = xml_obj.get_bridge(interface)

        p = subprocess.Popen(['brctl', 'delif', bridge, interface])
        p.wait()
        temp = p.returncode
        if temp != 0:
            print("Delete interface <name: {0}> failed".format(interface))

        return
