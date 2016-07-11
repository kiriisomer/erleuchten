# coding:utf-8

# prepare testing environment(vm, software, yeesan, etc.)

ENVVM_STATUS_UNKNOWN = 'unknown'
ENVVM_STATUS_STOP = 'stop'
ENVVM_STATUS_RUNNING = 'runnning'


def define():
    """define an environment"""


def prepare():
    """start an environment and install requested software"""


def stop():
    """force stop an environment"""


def remove():
    """fully delete an environment from disk"""


class VMTemplate(object):
    """VM template"""

    def __init__(self):
        self.name = ""

    def cerate(self):
        """add a template"""
        self._create_from_local_path()

    def remove(self):
        """remove a template from disk"""

    def _create_from_local_path(self):
        """"""


class EnvVM(object):
    """single VM"""

    def __init__(self):
        self.name = ""
        self.env_name = ""
        self.order = 1
        self.status = ENVVM_STATUS_UNKNOWN
        self.ip = ""
        self.ssh_user = "root"
        self.ssh_user_pswd = "111111"

    def spawn_from_template(self):
        """create VM from a template"""

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
