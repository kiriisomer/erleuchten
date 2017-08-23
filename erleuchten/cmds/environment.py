# coding:utf-8

# entry of environment

import sys
import argparse
import libvirt
from erleuchten.utils.error import ErleuchtenException
from erleuchten import environment


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-env')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'environment utility')

    p_create = sub_parsers.add_parser('create', help='create a environment')
    p_create.add_argument(
        '--name', help='environment name', required=True, type=str)
    p_create.set_defaults(func=cmd_create)

    p_remove = sub_parsers.add_parser('remove', help='remove a environment')
    p_remove.add_argument(
        '--name', help='environment name', required=True, type=str)
    p_remove.set_defaults(func=cmd_remove)

    p_start = sub_parsers.add_parser('start', help='start all environment vm')
    p_start.add_argument('--name', help='environment name',
                         required=True, type=str)
    p_start.set_defaults(func=cmd_start)

    p_stop = sub_parsers.add_parser('stop', help='stop all environment vm')
    p_stop.add_argument('--name', help='environment name',
                        required=True, type=str)
    p_stop.add_argument('--force', help='stop all environment vm forcely',
                        required=False,
                        action='store_true', default=False)
    p_stop.set_defaults(func=cmd_stop)

    p_add_vm = sub_parsers.add_parser('define-vm', help='define a vm, '
                                      'will be created later')
    p_add_vm.add_argument('--name', help='environment name',
                          required=True, type=str)
    p_add_vm.add_argument('--vm-name', help='vm name', required=True,
                          type=str, dest='vm_name')
    p_add_vm.add_argument('--vm-src-name', help='vm source name',
                          required=True, type=str, dest='vm_src_name')
    p_add_vm.add_argument('--manage-ifcfg-source',
                          help='manage interface file path',
                          required=False, type=str, dest='manage_ifcfg_source')
    p_add_vm.add_argument('--manage-if-name', help='manage interface name',
                          required=False, type=str, dest='manage_if_name')
    p_add_vm.add_argument('--manage-addr', help='manage address',
                          required=False, type=str, dest='manage_addr')
    p_add_vm.add_argument('--manage-mask', help='manage mask',
                          required=False, type=str, dest='manage_mask')
    p_add_vm.add_argument('--manage-gateway', help='manage gateway',
                          required=False, type=str, dest='manage_gateway')
    p_add_vm.add_argument('--manage-dns', help='manage dns',
                          required=False, type=str, dest='manage_dns')
    p_add_vm.add_argument('--storage-ifcfg-source',
                          help='storage interface file path', required=False,
                          type=str, dest='storage_ifcfg_source')
    p_add_vm.add_argument('--storage-if-name', help='storage interface name',
                          required=False, type=str, dest='storage_if_name')
    p_add_vm.add_argument('--storage-addr', help='storage address',
                          required=False, type=str, dest='storage_addr')
    p_add_vm.add_argument('--storage-mask', help='storage mask',
                          required=False, type=str, dest='storage_mask')
    p_add_vm.add_argument('--ssh-user', help='vm ssh user name',
                          required=False, type=str, dest='ssh_user')
    p_add_vm.add_argument('--ssh-password', help='vm ssh user password',
                          required=False, type=str, dest='ssh_password')
    p_add_vm.set_defaults(func=cmd_define_vm)

    p_set_vm = sub_parsers.add_parser('modify-vm', help='modify vm info')
    p_set_vm.add_argument('--name', help='environment name',
                          required=True, type=str)
    p_set_vm.add_argument('--vm-name', help='vm name',
                          required=True, type=str, dest='vm_name')
    p_set_vm.add_argument('--vm-src-name', help='vm source name',
                          required=False, type=str, dest='vm_src_name')
    p_set_vm.add_argument('--manage-ifcfg-source',
                          help='manage interface file path',
                          required=False, type=str, dest='manage_ifcfg_source')
    p_set_vm.add_argument('--manage-if-name', help='manage interface name',
                          required=False, type=str, dest='manage_if_name')
    p_set_vm.add_argument('--manage-addr', help='manage address',
                          required=False, type=str, dest='manage_addr')
    p_set_vm.add_argument('--manage-mask', help='manage mask',
                          required=False, type=str, dest='manage_mask')
    p_set_vm.add_argument('--manage-gateway', help='manage gateway',
                          required=False, type=str, dest='manage_gateway')
    p_set_vm.add_argument('--manage-dns', help='manage dns',
                          required=False, type=str, dest='manage_dns')
    p_set_vm.add_argument('--storage-ifcfg-source',
                          help='storage interface file path', required=False,
                          type=str, dest='storage_ifcfg_source')
    p_set_vm.add_argument('--storage-if-name', help='storage interface name',
                          required=False, type=str, dest='storage_if_name')
    p_set_vm.add_argument('--storage-addr', help='storage address',
                          required=False, type=str, dest='storage_addr')
    p_set_vm.add_argument('--storage-mask', help='storage mask',
                          required=False, type=str, dest='storage_mask')
    p_set_vm.add_argument('--ssh-user', help='vm ssh user name',
                          required=False, type=str, dest='ssh_user')
    p_set_vm.add_argument('--ssh-password', help='vm ssh user password',
                          required=False, type=str, dest='ssh_password')
    p_set_vm.set_defaults(func=cmd_modify_vm)

    p_del_vm = sub_parsers.add_parser('delete-vm', help='delete vm')
    p_del_vm.add_argument('--name', help='environment name',
                          required=True, type=str)
    p_del_vm.add_argument('--vm-name', help='vm name',
                          required=True, type=str, dest='vm_name')
    p_del_vm.add_argument('--rfd', help='delete vm permanently',
                          required=False, action='store_true',
                          default=False)
    p_del_vm.set_defaults(func=cmd_delete_vm)

    p_info_vm = sub_parsers.add_parser('vm-info', help='get environment '
                                       'including vm info')
    p_info_vm_group = p_info_vm.add_mutually_exclusive_group(required=True)
    p_info_vm_group.add_argument('--vm-name', help='vm name',
                                 type=str, dest='logo')
    p_info_vm_group.add_argument('--order', help='vm order', type=int,
                                 dest='logo')
    p_info_vm.add_argument('--name', help='environment name', required=True,
                           type=str, dest='name')
    p_info_vm.set_defaults(func=cmd_vm_info)

    p_list_env = sub_parsers.add_parser('list', help='list all environment')
    p_list_env.set_defaults(func=cmd_list)

    p_list_env_vm = sub_parsers.add_parser('list-vm', help='list environment '
                                           'vm name')
    p_list_env_vm.add_argument('--name', help='environment name',
                               required=True, type=str)
    p_list_env_vm.set_defaults(func=cmd_list_vm)

    p_ssh_cmd = sub_parsers.add_parser('sshcmd', help='process command in vm, '
                                       'using ssh')
    p_ssh_cmd_group = p_ssh_cmd.add_mutually_exclusive_group(required=True)
    p_ssh_cmd_group.add_argument('--vm-name', help='vm name',
                                 type=str, dest='logo')
    p_ssh_cmd_group.add_argument('--order', help='vm order',
                                 type=int, dest='logo')
    p_ssh_cmd.add_argument('--name', help='environment name',
                           dest='name', required=True, type=str)
    p_ssh_cmd.add_argument('--cmd', help='command, will process on vm '
                           'through ssh', required=True, type=str)
    p_ssh_cmd.set_defaults(func=cmd_process_ssh_cmd)

    p_ssh_put = sub_parsers.add_parser('sshput', help='put file to vm, '
                                       'using ssh')
    p_ssh_put_group = p_ssh_put.add_mutually_exclusive_group(required=True)
    p_ssh_put_group.add_argument('--vm-name', help='vm name',
                                 type=str, dest='logo')
    p_ssh_put_group.add_argument('--order', help='vm order in environment',
                                 type=int, dest='logo')
    p_ssh_put.add_argument('--name', help='environment name',
                           dest='name', required=True, type=str)
    p_ssh_put.add_argument('--src', help='local file path',
                           required=True, type=str)
    p_ssh_put.add_argument('--dst', help='remote file storage path',
                           required=True, type=str)
    p_ssh_put.set_defaults(func=cmd_ssh_put)

    p_ssh_get = sub_parsers.add_parser('sshget', help='get file from vm,'
                                       'using ssh')
    p_ssh_get_group = p_ssh_get.add_mutually_exclusive_group(required=True)
    p_ssh_get_group.add_argument('--vm-name', help='vm name',
                                 type=str, dest='logo')
    p_ssh_get_group.add_argument('--order', help='vm order in environment',
                                 type=int, dest='logo')
    p_ssh_get.add_argument('--name', help='environment name',
                           dest='name', required=True, type=str)
    p_ssh_get.add_argument('--src', help='remote file path',
                           required=True, type=str)
    p_ssh_get.add_argument('--dst', help='local file storage path',
                           required=True, type=str)
    p_ssh_get.set_defaults(func=cmd_ssh_get)

    p_init_all = sub_parsers.add_parser('init-all', help='initialize all vm')
    p_init_all.add_argument('--name', help='environment name', required=True,
                            type=str)
    p_init_all.set_defaults(func=init_all)

    p_poweron_vm = sub_parsers.add_parser('start-vm', help='start vm')
    p_poweron_vm.add_argument('--name', help='environment name', type=str,
                              required=True)
    p_poweron_vm_group = p_poweron_vm.add_mutually_exclusive_group(
        required=True)
    p_poweron_vm_group.add_argument('--vm-name', help='vm name',
                                    type=str, dest='logo')
    p_poweron_vm_group.add_argument('--order', help='vm order in environment',
                                    type=int, dest='logo')
    p_poweron_vm.set_defaults(func=poweron)

    p_poweroff_vm = sub_parsers.add_parser('shutdown-vm', help='shutdonwn vm')
    p_poweroff_vm.add_argument('--name', help='environment name', type=str,
                               required=True)
    p_poweroff_vm_group = p_poweroff_vm.add_mutually_exclusive_group(
        required=True)
    p_poweroff_vm_group.add_argument('--vm-name', help='vm name',
                                     type=str, dest='logo')
    p_poweroff_vm_group.add_argument('--order', help='vm order in environment',
                                     type=int, dest='logo')
    p_poweroff_vm.set_defaults(func=poweroff)

    p_destroy_vm = sub_parsers.add_parser('destroy-vm', help='destroy vm')
    p_destroy_vm.add_argument('--name', help='environment name', type=str,
                              required=True)
    p_destroy_vm_group = p_destroy_vm.add_mutually_exclusive_group(
        required=True)
    p_destroy_vm_group.add_argument('--vm-name', help='vm name',
                                    type=str, dest='logo')
    p_destroy_vm_group.add_argument('--order', help='vm order in environment',
                                    type=int, dest='logo')
    p_destroy_vm.set_defaults(func=destroy)

    p_list_disks = sub_parsers.add_parser('list-disk', help='list disk of vm')
    p_list_disks.add_argument('--name', help='environment name', type=str,
                              required=True)
    p_list_disks_group = p_list_disks.add_mutually_exclusive_group(
        required=True)
    p_list_disks_group.add_argument('--vm-name', help='vm name',
                                    type=str, dest='logo')
    p_list_disks_group.add_argument('--order', help='vm order in environment',
                                    type=int, dest='logo')
    p_list_disks.set_defaults(func=list_disks)

    p_list_ifs = sub_parsers.add_parser('list-ifs',
                                        help='list interfaces of vm')
    p_list_ifs.add_argument('--name', help='environment name', type=str,
                            required=True)
    p_list_ifs_group = p_list_ifs.add_mutually_exclusive_group(required=True)
    p_list_ifs_group.add_argument('--vm-name', help='vm name',
                                  type=str, dest='logo')
    p_list_ifs_group.add_argument('--order', help='vm order in environment',
                                  type=int, dest='logo')
    p_list_ifs.set_defaults(func=list_ifs)

    p_undefine_vm = sub_parsers.add_parser('undefine-vm',
                                           help='undefine a vm')
    p_undefine_vm.add_argument('--name', help='environment name', type=str,
                               required=True)
    p_undefine_vm_group = p_undefine_vm.add_mutually_exclusive_group(
        required=True)
    p_undefine_vm_group.add_argument('--vm-name', help='vm name',
                                     type=str, dest='logo')
    p_undefine_vm_group.add_argument('--order', help='vm order in environment',
                                     type=int, dest='logo')
    p_undefine_vm.set_defaults(func=undefine_vm)

    p_attach_disk = sub_parsers.add_parser('attach-disk',
                                           help='attach disk to a vm')
    p_attach_disk.add_argument('--name', help='environment name', type=str,
                               required=True)
    p_attach_disk_group = p_attach_disk.add_mutually_exclusive_group(
        required=True)
    p_attach_disk_group.add_argument('--vm-name', help='vm name',
                                     type=str, dest='logo')
    p_attach_disk_group.add_argument('--order', help='vm order in environment',
                                     type=int, dest='logo')
    p_attach_disk.add_argument('--src', help='disk source path',
                               required=True, type=str)
    p_attach_disk.add_argument('--tgt', help='disk target path',
                               required=True, type=str)
    p_attach_disk.add_argument('--fmt', help='disk format',
                               required=True, type=str)
    p_attach_disk.set_defaults(func=attach_disk)

    p_detach_disk = sub_parsers.add_parser('detach-disk',
                                           help='attach disk to a vm')
    p_detach_disk.add_argument('--name', help='environment name', type=str,
                               required=True)
    p_detach_disk_group = p_detach_disk.add_mutually_exclusive_group(
        required=True)
    p_detach_disk_group.add_argument('--vm-name', help='vm name',
                                     type=str, dest='logo')
    p_detach_disk_group.add_argument('--order', help='vm order in environment',
                                     type=int, dest='logo')
    p_detach_disk.add_argument('--tgt', help='disk target path',
                               required=True, type=str)
    p_detach_disk.set_defaults(func=detach_disk)

    p_connect_if = sub_parsers.add_parser(
        'connect-if', help='restore the connection of a interface')
    p_connect_if.add_argument('--name', help='environment name',
                              type=str, required=True)
    p_connect_if_group = p_connect_if.add_mutually_exclusive_group(
        required=True)
    p_connect_if_group.add_argument('--vm-name', help='vm name',
                                    type=str, dest='logo')
    p_connect_if_group.add_argument('--order',
                                    help='vm order in environment',
                                    type=int, dest='logo')
    p_connect_if.add_argument('--interface', help='interface')
    p_connect_if.set_defaults(func=connect_if)

    p_disconnect_if = sub_parsers.add_parser(
        'disconnect-if', help='cut off the connection of a interface')
    p_disconnect_if.add_argument('--name', help='environment name',
                                 type=str, required=True)
    p_disconnect_if_group = p_disconnect_if.add_mutually_exclusive_group(
        required=True)
    p_disconnect_if_group.add_argument('--vm-name', help='vm name',
                                       type=str, dest='logo')
    p_disconnect_if_group.add_argument('--order',
                                       help='vm order in environment',
                                       type=int, dest='logo')
    p_disconnect_if.add_argument('--interface', help='interface',
                                 type=str, required=True)
    p_disconnect_if.set_defaults(func=disconnect_if)

    args = main_parser.parse_args()
    try:
        args.func(args)
    except (IOError, TypeError, ValueError, OSError, SystemError,
            IndexError, ErleuchtenException, libvirt.libvirtError), \
            diag:
        retval = str(diag)
        return retval
#        err = os.path.join(conf.get("PATH_ENVIRONMENT"),
#                           "error.txt")
#        print("Exception occured")
#        print("Exception >>>> err")
#        print("Error Output path is: %s" % err)
#        t = time.strftime('%Y%m%d_%X', time.localtime())
#        with open(err, 'a+') as fp:
#            fp.write(t + "  " + retval)
#            fp.write("\n")


def cmd_create(args):
    environment.create_env(args.name)


def cmd_remove(args):
    environment.remove_env(args.name)


def cmd_start(args):
    environment.env_start(args.name)


def cmd_stop(args):
    environment.env_stop(args.name, args.force)


def cmd_define_vm(args):
    vm_info_dict = {
        "vm-name": args.vm_name,
        "vm-src-name": args.vm_src_name,
        "manage_ifcfg_source": args.manage_ifcfg_source,
        "manage-if-name": args.manage_if_name,
        "manage-addr": args.manage_addr,
        "manage-mask": args.manage_mask,
        "manage-gateway": args.manage_gateway,
        "manage-dns": args.manage_dns,
        "storage_ifcfg_source": args.storage_ifcfg_source,
        "storage-if-name": args.storage_if_name,
        "storage-addr": args.storage_addr,
        "storage-mask": args.storage_mask,
        "ssh_user": args.ssh_user,
        "ssh_password": args.ssh_password,
    }
    environment.env_define_vm(args.name, vm_info_dict)


def cmd_modify_vm(args):
    vm_info_dict = {
        "vm-name": args.vm_name,
        "vm-src-name": args.vm_src_name,
        "manage_ifcfg_source": args.manage_ifcfg_source,
        "manage-if-name": args.manage_if_name,
        "manage-addr": args.manage_addr,
        "manage-mask": args.manage_mask,
        "manage-gateway": args.manage_gateway,
        "manage-dns": args.manage_dns,
        "storage_ifcfg_source": args.storage_ifcfg_source,
        "storage-if-name": args.storage_if_name,
        "storage-addr": args.storage_addr,
        "storage-mask": args.storage_mask,
        "ssh_user": args.ssh_user,
        "ssh_password": args.ssh_password,
    }
    environment.env_modify_vm(args.name, vm_info_dict)


def cmd_delete_vm(args):
    environment.env_delete_vm(
        args.name, args.vm_name, args.rfd)


def cmd_vm_info(args):
    result = environment.env_get_vm_info(args.name, args.logo)
    for i, j in result.items():
        print '%s  %s' % (i, j)


def cmd_list(args):
    result = environment.list_env()
    print '\n'.join(result)


def cmd_list_vm(args):
    result = environment.env_list_vm(args.name)
    print '\n'.join(result)


def cmd_process_ssh_cmd(args):
    returncode = environment.env_ssh_cmd(args.name, args.logo, args.cmd)
    sys.exit(returncode)


def cmd_ssh_put(args):
    environment.env_ssh_put(
        args.name, args.logo, args.src, args.dst)


def cmd_ssh_get(args):
    environment.env_ssh_get(
        args.name, args.logo, args.src, args.dst)


def init_all(args):
    environment.init_all_vm(args.name)


def poweron(args):
    environment.vm_poweron(args.name, args.logo)


def poweroff(args):
    environment.vm_poweroff(args.name, args.logo)


def destroy(args):
    environment.vm_destroy(args.name, args.logo)


def list_disks(args):
    environment.vm_list_disks(args.name, args.logo)


def list_ifs(args):
    environment.vm_list_ifs(args.name, args.logo)


def undefine_vm(args):
    environment.vm_undefine(args.name, args.logo)


def attach_disk(args):
    environment.vm_attach_disk(args.name, args.logo,
                               args.src, args.tgt, args.fmt)


def detach_disk(args):
    environment.vm_detach_disk(args.name, args.logo, args.tgt)


def connect_if(args):
    environment.vm_connect_if(args.name, args.logo, args.interface)


def disconnect_if(args):
    environment.vm_disconnect_if(args.name, args.logo, args.interface)
