# coding:utf-8

# prepare testing environment(vm, software, yeesan, etc.)
import os

import shutil

from erleuchten import conf


VMTEMPLATE_STATUS_UNKNOWN = 'unknown'
VMTEMPLATE_STATUS_NORMAL = 'normal'
VMTEMPLATE_STATUS_BAD = 'bad'

ENVVM_STATUS_UNKNOWN = 'unknown'
ENVVM_STATUS_STOP = 'stop'
ENVVM_STATUS_RUNNING = 'runnning'


# def define():
#     """define an environment"""


# def prepare():
#     """start an environment and install requested software"""


# def stop():
#     """force stop an environment"""


# def remove():
#     """fully delete an environment from disk"""


class VMTemplate(object):
    """VM template"""

    def __init__(self):
        self.name = ""
        self.xml = None
        self.status = VMTEMPLATE_STATUS_UNKNOWN
        # self.device_path_dict = {}

    def initial(self, name):
        """init class by vm_template's name"""
        self.name = name
        xml_path = os.path.join(conf.PATH_VM_TEMPLATE, self.name,
                                "%s.xml" % self.name)

        # self.device_path_dict = {}

    def cerate(self):
        """add a template"""
        self._create_from_local_xml()

    def remove(self):
        """remove a template from disk"""
        # remove xml file and related disk img
        for i in self.device_path_dict.values():
            os.unlink(i)
        os.unlink(self.xml.xml_path)

        # reset param
        self.name = ""
        self.status = VMTEMPLATE_STATUS_UNKNOWN
        self.xml = None
        # self.device_path_dict = {}

    def _create_from_local_xml(self, name, xml_path, move_dev_files=False):
        """"""
        self.name = name
        self.xml_path = os.path.join(conf.PATH_VM_TEMPLATE, self.name,
                                     "%s.xml" % self.name)
        # 复制xml文件到目录中。
        shutil.copy(xml_path, self.xml_path)
        if move_dev_files:
            for i in

    def copy(self, src_obj):
        """copy and create a new VMTemplate"""




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

    def initial(self, name):
        """init class by vm_template's name"""
        self.name = name

    def create(self):
        self._spawn_from_template()

    def _spawn_from_template(self):
        """create VM from a VM_template"""

    def power_on(self):
        """"""

    def power_off(self):
        """"""

    def insert_disk(self):
        """"""

    def eject_disk(self):
        """"""


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
