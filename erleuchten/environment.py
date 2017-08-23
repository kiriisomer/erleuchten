# coding:utf-8

# prepare testing environment(vm, software, etc.)
import os
import libvirt
import StringIO
import subprocess
import time
import shutil

from erleuchten.utils import conf, remote
from erleuchten.utils.error import ErleuchtenException
from erleuchten.utils.error import Errno
from erleuchten.utils.xml import EnvConf
from erleuchten.utils.xml import VMXML
from erleuchten.utils.util import create_dir
from erleuchten.vm import VM

HYPERVISOR_URI = "qemu:///system"

ENV_STATUS_UNKNOWN = 'unknown'
ENV_STATUS_READY = 'ready'
ENV_STATUS_RUNNING = 'running'
ENV_STATUS_NOT_ALL_RUNNING = 'not all vm running'
ENV_STATUS_STOP = 'stop'


# ##############################################################################
#
# ##############################################################################
def create_env(name):
    if os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                   "%s.conf" % name)):
        # 已经存在了
        print("{name} already existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_ENV_ALREADY_EXISTS)
        return

    env_obj = Environment()
    env_obj.load_conf(name)
    env_obj.initial(name)
    env_obj.change_status_ready()
    env_obj.save_conf()
    print("<Env name: %s> created" % name)


def remove_env(name):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)
    if env_obj.status == ENV_STATUS_RUNNING:
        print("env is running")
    else:
        shutil.rmtree(os.path.join(conf.get("PATH_ENVIRONMENT"), name))
        print("remove env succeed")


def env_start(name):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)
    if env_obj.status == ENV_STATUS_RUNNING:
        print("env has started")
        env_obj.start_all_vm()
    else:
        env_obj.change_status_running()
        env_obj.start_all_vm()
        env_obj.save_conf()


def env_stop(name, force):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if env_obj.status == ENV_STATUS_STOP:
        print("env has stopped")
        env_obj.shutdown_all_vm(force)
    else:
        env_obj.change_status_stop()
        env_obj.shutdown_all_vm(force)
        env_obj.save_conf()
        print("stop env succeed")


def env_define_vm(name, vm_info_dict):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if env_obj.status == ENV_STATUS_READY:
        env_obj.change_status_stop()
    env_obj.add_domain_desc(vm_info_dict.get("vm-name", ""),
                            vm_info_dict.get("vm-src-name", ""),
                            vm_info_dict.get("manage_ifcfg_source", ""),
                            vm_info_dict.get("manage-if-name", ""),
                            vm_info_dict.get("manage-addr", ""),
                            vm_info_dict.get("manage-mask", ""),
                            vm_info_dict.get("manage-gateway", ""),
                            vm_info_dict.get("manage-dns", ""),
                            vm_info_dict.get("storage_ifcfg_source", ""),
                            vm_info_dict.get("storage-if-name", ""),
                            vm_info_dict.get("storage-addr", ""),
                            vm_info_dict.get("storage-mask", ""),
                            vm_info_dict.get("ssh_user", ""),
                            vm_info_dict.get("ssh_password", ""))
    env_obj.save_conf()
    print("<VM name: %s> defined" % vm_info_dict["vm-name"])


def env_modify_vm(name, vm_info_dict):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if env_obj.status == ENV_STATUS_READY:
        env_obj.change_status_stop()
    env_obj.modify_domain_desc(vm_info_dict.get("vm-name", ""),
                               vm_info_dict.get("vm-src-name", ""),
                               vm_info_dict.get("manage_ifcfg_source", ""),
                               vm_info_dict.get("manage-if-name", ""),
                               vm_info_dict.get("manage-addr", ""),
                               vm_info_dict.get("manage-mask", ""),
                               vm_info_dict.get("manage-gateway", ""),
                               vm_info_dict.get("manage-dns", ""),
                               vm_info_dict.get("storage_ifcfg_source", ""),
                               vm_info_dict.get("storage-if-name", ""),
                               vm_info_dict.get("storage-addr", ""),
                               vm_info_dict.get("storage-mask", ""),
                               vm_info_dict.get("ssh_user", ""),
                               vm_info_dict.get("ssh_password", ""))
    env_obj.save_conf()
    print("modify vm succeed")


def env_delete_vm(name, vm_name, rfd):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if (env_obj.status == ENV_STATUS_RUNNING) or \
       (env_obj.status == ENV_STATUS_NOT_ALL_RUNNING):
        print("before delete you should stop all vm")
        env_obj.save_conf()
    else:
        env_obj.change_status_stop()
        env_obj.remove_domain_desc(vm_name, rfd)
        env_obj.save_conf()
        print("delete vm succeed")


def env_get_vm_info(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.save_conf()
    return env_obj.get_vm_info(logo)


def list_env():
    if not os.path.exists(conf.get('PATH_ENVIRONMENT')):
        create_dir(conf.get('PATH_ENVIRONMENT'))
    result = []
    for i in os.listdir(conf.get('PATH_ENVIRONMENT')):
        try:
            if os.path.isfile(os.path.join(conf.get('PATH_ENVIRONMENT'), i,
                                           "%s.conf" % i)):
                result.append(i)
        except OSError:
            continue
    return result


def env_list_vm(name):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.save_conf()
    return env_obj.get_vm_list()


def env_ssh_cmd(name, logo, cmd):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.save_conf()
    return env_obj.remote_cmd(logo, cmd)


def env_ssh_put(name, logo, src, dst):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.save_conf()
    return env_obj.remote_put(logo, src, dst)


def env_ssh_get(name, logo, src, dst):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.save_conf()
    return env_obj.remote_get(logo, src, dst)


def init_all_vm(name):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.initial_all_vm()
    env_obj.change_status_stop()
    env_obj.save_conf()
    print("<Env name: %s> initialized (inside init_all_vm)" % name)


def vm_poweron(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if env_obj.status == ENV_STATUS_RUNNING:
        print("vm has been started")
        env_obj.poweron_vm(logo)
    else:
        env_obj.change_status_not_all_running()
        env_obj.poweron_vm(logo)
        env_obj.save_conf()
        print("poweron vm succeed")


def vm_poweroff(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if env_obj.status == ENV_STATUS_STOP:
        print("vm has been stopped")
        env_obj.poweroff_vm(logo)
    else:
        env_obj.change_status_not_all_stop()
        env_obj.poweroff_vm(logo)
        env_obj.save_conf()
        print("poweroff vm succeed")


def vm_destroy(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    if env_obj.status == ENV_STATUS_STOP:
        print("vm has been stopped")
        env_obj.destroy_vm(logo)
    else:
        env_obj.change_status_not_all_stop()
        env_obj.destroy_vm(logo)
        env_obj.save_conf()
        print("destroy vm succeed")


def vm_list_disks(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.list_disks_vm(logo)
    env_obj.save_conf()


def vm_list_ifs(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.list_ifs_vm(logo)
    env_obj.save_conf()


def vm_undefine(name, logo):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.undefine_vm(logo)
    env_obj.save_conf()


def vm_attach_disk(name, logo, src, tgt, fmt):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.attach_disk_vm(logo, src, tgt, fmt)
    env_obj.save_conf()


def vm_detach_disk(name, logo, tgt):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.detach_disk_vm(logo, tgt)
    env_obj.save_conf()


def vm_connect_if(name, logo, interface):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.connect_if_vm(logo, interface)
    env_obj.save_conf()


def vm_disconnect_if(name, logo, interface):
    if not os.path.exists(os.path.join(conf.get('PATH_ENVIRONMENT'), name,
                                       "%s.conf" % name)):
        # env不存在
        print("env {name} not existed".format(**{'name': name}))
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_ENV)
        return
    env_obj = Environment()
    env_obj.load_conf(name)

    env_obj.disconnect_if_vm(logo, interface)
    env_obj.save_conf()


# ##############################################################################
#
# ##############################################################################


class Environment(object):
    """an environment is a series of virtual machines."""

    def __init__(self):
        self.name = ""
        self.vm_info_list = []   # [{}, {}]
        self.status = ENV_STATUS_UNKNOWN
        self.conf_obj = None
        self.init_script_obj = None
        self.vm_name_list = []

    def initial(self, name):
        """初始化一个新的对象"""
        self.name = name

    def load_conf(self, name):
        """打开配置文件，读取配置初始化"""
        self.name = name
        conf_obj = EnvConf(
            os.path.join(
                conf.get('PATH_ENVIRONMENT'), self.name,
                "%s.conf" % self.name), self.name)
        self.conf_obj = conf_obj
        # 如果打开空文件，或记载名字错误，则无法继续下去
        if conf_obj.xml_root_obj is None and conf_obj.get_name() is None:
            #   raise ErleuchtenException(error=Errno.ERRNO_XML_OPEN_CONF_FAILED)
            return
        self.conf_dict = conf_obj.load_config()
        self.status = self.conf_dict["status"]
        self.vm_info_list = self.conf_dict["vm_info_list"]

    def save_conf(self):
        """保存配置到文件"""
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        self.conf_dict = {
            "name": self.name,
            "status": self.status,
            "vm_info_list": self.vm_info_list,
        }
        self.conf_obj.save_config(self.conf_dict)

    def add_domain_desc(self, vm_name, vm_src_name,
                        manage_ifcfg_source,
                        manage_if_name, manage_addr, manage_mask,
                        manage_gateway, manage_dns, storage_ifcfg_source,
                        storage_if_name, storage_addr, storage_mask,
                        ssh_user, ssh_password):
        """添加一个虚拟机描述"""
        # 检查是否已经添加过
        if vm_name in [x['vm_name'] for x in self.vm_info_list]:
            print("vm has been define defined")
            raise ErleuchtenException(errno=Errno.ERRNO_VM_HAS_BEEN_DEFINED)
            return

        desc_dict = {
            "vm_name": vm_name,
            "vm_src_name": vm_src_name,
            "manage_ifcfg_source": manage_ifcfg_source,
            "manage_if_name": manage_if_name,
            "manage_addr": manage_addr,
            "manage_mask": manage_mask,
            "manage_gateway": manage_gateway,
            "manage_dns": manage_dns,
            "storage_ifcfg_source": storage_ifcfg_source,
            "storage_if_name": storage_if_name,
            "storage_addr": storage_addr,
            "storage_mask": storage_mask,
            "ssh_user": ssh_user,
            "ssh_password": ssh_password,
        }
        self.vm_info_list.append(desc_dict)

    def modify_domain_desc(self, vm_name, vm_src_name,
                           manage_ifcfg_source, manage_if_name, manage_addr,
                           manage_mask, manage_gateway, manage_dns,
                           storage_ifcfg_source, storage_if_name, storage_addr,
                           storage_mask, ssh_user, ssh_password):
        """修改一个虚拟机描述"""
        desc_dict = {}
        if vm_name is not None:
            desc_dict["vm_name"] = vm_name
        if vm_src_name is not None:
            desc_dict["vm_src_name"] = vm_src_name
        if manage_ifcfg_source is not None:
            desc_dict["manage_ifcfg_source"] = manage_ifcfg_source
        if manage_if_name is not None:
            desc_dict["manage_if_name"] = manage_if_name
        if manage_addr is not None:
            desc_dict["manage_addr"] = manage_addr
        if manage_mask is not None:
            desc_dict["manage_mask"] = manage_mask
        if manage_gateway is not None:
            desc_dict["manage_gateway"] = manage_gateway
        if manage_dns is not None:
            desc_dict["manage_dns"] = manage_dns
        if storage_ifcfg_source is not None:
            desc_dict["storage_ifcfg_source"] = storage_ifcfg_source
        if storage_if_name is not None:
            desc_dict["storage_if_name"] = storage_if_name
        if storage_addr is not None:
            desc_dict["storage_addr"] = storage_addr
        if storage_mask is not None:
            desc_dict["storage_mask"] = storage_mask
        if ssh_user is not None:
            desc_dict["ssh_user"] = ssh_user
        if ssh_password is not None:
            desc_dict["ssh_password"] = ssh_password

        for i in range(len(self.vm_info_list)):
            if self.vm_info_list[i]["vm_name"] == vm_name:
                self.vm_info_list[i].update(desc_dict)
                return
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def initial_all_vm(self):
        """initial env VMs"""
        for i in self.vm_info_list:
            a = VM(i["vm_name"])
            a.clone(i)

    def start_all_vm(self):
        """poweron env VMs"""
        for i in self.vm_info_list:
            try:
                a = VM(i["vm_name"])
                a.poweron()
            except libvirt.libvirtError, e:
                if e.err[0] == libvirt.VIR_ERR_OPERATION_INVALID:
                    # domain is already running
                    continue
                raise

        for i in self.vm_info_list:
            fd = open("/dev/null", 'w')
            t = time.time()
            while (time.time() < t + 300):
                p = subprocess.Popen(["ping", "-c", "1", i["manage_addr"]],
                                     stdout=fd)
                p.wait()
                exit_code = p.returncode
                if exit_code == 0:
                    fd.close()
                    print "<VM name: %s> Manage address is ok" % i["vm_name"]
                    break
                time.sleep(10)
            else:
                fd.close()
                print "vm haven't started or manage addr Error"
                raise ErleuchtenException(errno=Errno.ERRNO_WAIT_VM_START_ERROR)

        for i in self.vm_info_list:
            fd = open("/dev/null", 'w')
            t = time.time()
            while (time.time() < t + 300):
                p = subprocess.Popen(["ping", "-c", "1", i["storage_addr"]],
                                     stdout=fd)
                p.wait()
                exit_code = p.returncode
                if exit_code == 0:
                    fd.close()
                    print "<VM name: %s> Storage address is ok" % i["vm_name"]
                    break
                time.sleep(10)
            else:
                fd.close()
                print "vm haven't started or storage addr Error"
                raise ErleuchtenException(errno=Errno.ERRNO_WAIT_VM_START_ERROR)

    def shutdown_all_vm(self, force):
        """shutdown env VMs"""
        if force is False:
            for i in self.vm_info_list:
                try:
                    a = VM(i["vm_name"])
                    a.poweroff()
                except libvirt.libvirtError, e:
                    if e.err[0] == libvirt.VIR_ERR_OPERATION_INVALID:
                        # domain is not running
                        continue
                    raise
        else:
            for i in self.vm_info_list:
                try:
                    a = VM(i["vm_name"])
                    a.destroy()
                except libvirt.libvirtError, e:
                    if e.err[0] == libvirt.VIR_ERR_OPERATION_INVALID:
                        # domain is not running
                        continue
                    raise

    def remove_domain_desc(self, vm_name, rfd):
        """remove VM from environment"""
        if rfd is False:
            for i in range(len(self.vm_info_list)):
                if self.vm_info_list[i]["vm_name"] == vm_name:
                    del self.vm_info_list[i]
                    break
        else:
            conn = libvirt.open(HYPERVISOR_URI)
            for i in range(len(self.vm_info_list)):
                if self.vm_info_list[i]["vm_name"] == vm_name:
                    dom = conn.lookupByName(self.vm_info_list[i]["vm_name"])

                    disk = []
                    xmldata = dom.XMLDesc(0)
                    xml_obj = VMXML(StringIO.StringIO(xmldata))
                    disk = xml_obj.get_device_path_list()
                    for x in disk:
                        try:
                            os.remove(x)
                        except OSError, e:
                            raise e
                else:
                    pass

    def get_vm_list(self):
        return [x['vm_name'] for x in self.vm_info_list]

    def get_vm_info(self, logo):
        if type(logo) == int:
            t = logo - 1
            return self.vm_info_list[t]
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    return i
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def remote_cmd(self, logo, cmd):
        if type(logo) == int:
            t = logo - 1
            return remote.fabric_command(self.vm_info_list[t]["manage_addr"],
                                         self.vm_info_list[t]["ssh_user"],
                                         self.vm_info_list[t]["ssh_password"],
                                         cmd)
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    return remote.fabric_command(i["manage_addr"],
                                                 i["ssh_user"],
                                                 i["ssh_password"], cmd)
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def remote_put(self, logo, local_src, remote_dst):
        if type(logo) == int:
            t = logo - 1
            return remote.fabric_put(self.vm_info_list[t]["manage_addr"],
                                     self.vm_info_list[t]["ssh_user"],
                                     self.vm_info_list[t]["ssh_password"],
                                     local_src, remote_dst)
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    return remote.fabric_put(i["manage_addr"], i["ssh_user"],
                                             i["ssh_password"], local_src,
                                             remote_dst)
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def remote_get(self, logo, remote_src, local_dst):
        if type(logo) == int:
            t = logo - 1
            return remote.fabric_get(self.vm_info_list[t]["manage_addr"],
                                     self.vm_info_list[t]["ssh_user"],
                                     self.vm_info_list[t]["ssh_password"],
                                     remote_src, local_dst)
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    return remote.fabric_get(i["manage_addr"], i["ssh_user"],
                                             i["ssh_password"], remote_src,
                                             local_dst)
        raise ErleuchtenException(errno=Errno.ERRNO_CANNOT_FIND_VM_IN_ENV)

    def change_status_running(self):
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        self.status = ENV_STATUS_RUNNING

    def change_status_stop(self):
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        self.status = ENV_STATUS_STOP

    def change_status_ready(self):
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        self.status = ENV_STATUS_READY

    def change_status_not_all_running(self):
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        self.status = ENV_STATUS_NOT_ALL_RUNNING

    def change_status_not_all_stop(self):
        if self.conf_obj is None:
            raise ErleuchtenException(errno=Errno.ERRNO_SAVE_PATH_NOT_SPECIFY)
        self.status = ENV_STATUS_NOT_ALL_RUNNING

    def poweron_vm(self, logo):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.poweron()
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.poweron()
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exists")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def poweroff_vm(self, logo):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.poweroff()
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.poweroff()
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def destroy_vm(self, logo):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.destroy()
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.destroy()
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def list_disks_vm(self, logo):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                print a.list_disks()
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        print a.list_disks()
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def list_ifs_vm(self, logo):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                print a.list_interfaces()
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        print a.list_interfaces()
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def undefine_vm(self, logo):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.undefine_domain()
                print("undefine vm succeed")
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.undefine_domain()
                        print("undefine vm succeed")
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def attach_disk_vm(self, logo, src, tgt, fmt):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.attach_disk(src, tgt, fmt)
                print("attach disk to vm succeed")
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.attach_disk(src, tgt, fmt)
                        print("attach disk to vm succeed")
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def detach_disk_vm(self, logo, tgt):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.detach_disk(tgt)
                print("detach disk from vm succeed")
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.detach_disk(tgt)
                        print("detach disk from vm succeed")
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def connect_if_vm(self, logo, interface):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.connect_interface(interface)
                print("connect if succeed")
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.connect_interface(interface)
                        print("connect if succeed")
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)

    def disconnect_if_vm(self, logo, interface):
        if type(logo) == int:
            t = logo - 1
            try:
                a = VM(self.vm_info_list[t]["vm_name"])
                a.disconnect_interface(interface)
                print("disconnect if succeed")
            except libvirt.libvirtError, e:
                print(e)
                raise
        else:
            for i in self.vm_info_list:
                if i["vm_name"] == logo:
                    try:
                        a = VM(i["vm_name"])
                        a.disconnect_interface(interface)
                        print("disconnect if succeed")
                        break
                    except libvirt.libvirtError, e:
                        print(e)
                        raise
            else:
                print("vm not exist")
                raise ErleuchtenException(errno=Errno.ERRNO_VM_NOT_EXISTS)
