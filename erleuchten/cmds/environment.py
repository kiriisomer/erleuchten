# coding:utf-8

# entry of environment

import argparse
from erleuchten import environment


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-env')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'environment utility')

    p_create = sub_parsers.add_parser('create', help='create a environment')
    p_create.add_argument('--name', help='environment name', required=True)
    p_create.set_defaults(func=cmd_create)

    p_add_vm = sub_parsers.add_parser('define-vm', help='define a vm, '
                                      'will be created later')
    p_add_vm.add_argument('--name', help='environment name', required=True)
    p_add_vm.add_argument('--vm-name', help='vm name', required=True,
                          dest='vm_name')
    p_add_vm.add_argument('--vm-src-name', help='vm source name',
                          required=True, dest='vm_src_name')
    p_add_vm.add_argument('--vm-if-name', help='vm interface name',
                          required=False, dest='vm_if_name')
    p_add_vm.add_argument('--vm-addr', help='vm address', required=False,
                          dest='vm_addr')
    p_add_vm.add_argument('--vm-mask', help='vm mask', required=False,
                          dest='vm_mask')
    p_add_vm.add_argument('--vm-gateway', help='vm gateway', required=False,
                          dest='vm_gateway')
    p_add_vm.add_argument('--vm-dns', help='vm dns', required=False,
                          dest='vm_dns')
    p_add_vm.add_argument('--vm-user', help='vm ssh user name', required=False,
                          dest='vm_user')
    p_add_vm.add_argument('--vm-password', help='vm ssh user password',
                          required=False, dest='vm_password')
    p_add_vm.set_defaults(func=cmd_define_vm)

    p_set_vm = sub_parsers.add_parser('modify-vm', help='modify vm info')
    p_set_vm.add_argument('--name', help='environment name', required=True)
    p_set_vm.add_argument('--vm-name', help='vm name', required=True,
                          dest='vm_name')
    p_set_vm.add_argument('--vm-src-name', help='vm source name',
                          required=True, dest='vm_src_name')
    p_set_vm.add_argument('--vm-if-name', help='vm interface name',
                          required=False, dest='vm_if_name')
    p_set_vm.add_argument('--vm-addr', help='vm address', required=False,
                          dest='vm_addr')
    p_set_vm.add_argument('--vm-mask', help='vm mask', required=False,
                          dest='vm_mask')
    p_set_vm.add_argument('--vm-gateway', help='vm gateway', required=False,
                          dest='vm_gateway')
    p_set_vm.add_argument('--vm-dns', help='vm dns', required=False,
                          dest='vm_dns')
    p_set_vm.add_argument('--vm-user', help='vm ssh user name', required=False,
                          dest='vm_user')
    p_set_vm.add_argument('--vm-password', help='vm ssh user password',
                          required=False, dest='vm_password')
    p_set_vm.set_defaults(func=cmd_modify_vm)

    p_set_vm = sub_parsers.add_parser('delete-vm', help='delete environment '
                                      'including vm')
    p_set_vm.add_argument('--name', help='environment name', required=True)
    p_set_vm.add_argument('--vm-name', help='vm name', required=True,
                          dest='vm_name')
    p_set_vm.set_defaults(func=cmd_delete_vm)

    p_info_vm = sub_parsers.add_parser('vm-info', help='get environment '
                                       'including vm info')
    p_info_vm.add_argument('--name', help='environment name', required=True)
    p_info_vm.add_argument('--vm-name', help='vm name', required=True,
                           dest='vm_name')
    p_info_vm.set_defaults(func=cmd_vm_info)

    p_init_vm = sub_parsers.add_parser('vm-init', help='get environment '
                                       'including vm info')
    p_init_vm.add_argument('--name', help='environment name', required=True)
    p_init_vm.set_defaults(func=cmd_vm_init_all)

    p_list_env = sub_parsers.add_parser('list', help='list all environment')
    p_list_env.set_defaults(func=cmd_list)

    p_list_env_vm = sub_parsers.add_parser('list-vm', help='list environment '
                                           'vm name')
    p_list_env_vm.add_argument('--name', help='environment name',
                               required=True)
    p_list_env_vm.set_defaults(func=cmd_list_vm)

    p_ssh_cmd = sub_parsers.add_parser('sshcmd', help='process command in vm, '
                                       'using ssh')
    p_ssh_cmd.add_argument('--name', help='environment name',
                           required=True)
    p_ssh_cmd.add_argument('--vm-name', help='environment name',
                           dest='vm_name', required=True)
    p_ssh_cmd.add_argument('--cmd', help='command, will process on vm '
                           'through ssh', required=True)
    p_ssh_cmd.set_defaults(func=cmd_process_ssh_cmd)

    p_ssh_put = sub_parsers.add_parser('sshput', help='put file to vm, '
                                       'using ssh')
    p_ssh_put.add_argument('--name', help='environment name',
                           required=True)
    p_ssh_put.add_argument('--vm-name', help='environment name',
                           dest='vm_name', required=True)
    p_ssh_put.add_argument('--src', help='local file path', required=True)
    p_ssh_put.add_argument('--dst', help='remote file storage path',
                           required=True)
    p_ssh_put.set_defaults(func=cmd_ssh_put)

    p_ssh_get = sub_parsers.add_parser('sshget', help='get file from vm,'
                                       'using ssh')
    p_ssh_get.add_argument('--name', help='environment name',
                           required=True)
    p_ssh_get.add_argument('--vm-name', help='environment name',
                           dest='vm_name', required=True)
    p_ssh_get.add_argument('--src', help='remote file path', required=True)
    p_ssh_get.add_argument('--dst', help='local file storage path',
                           required=True)
    p_ssh_get.set_defaults(func=cmd_ssh_get)

    p_remove = sub_parsers.add_parser('remove', help='remove a environment')
    p_remove.add_argument('--name', help='environment name', required=True)
    p_remove.set_defaults(func=cmd_remove)

    p_start = sub_parsers.add_parser('start', help='start all environment vm')
    p_start.add_argument('--name', help='environment name', required=True)
    p_start.set_defaults(func=cmd_start)

    p_stop = sub_parsers.add_parser('stop', help='stop all environment vm')
    p_stop.add_argument('--name', help='environment name', required=True)
    p_stop.set_defaults(func=cmd_stop)

    args = main_parser.parse_args()
    args.func(args)


def cmd_create(args):
    environment.create_env(args.name)


def cmd_define_vm(args):
    vm_info_dict = {
        "name": args.vm_name,
        "src_name": args.vm_src_name,
        "if_name": args.vm_if_name,
        "addr": args.vm_addr,
        "mask": args.vm_mask,
        "gateway": args.vm_gateway,
        "dns": args.vm_dns,
        "ssh_user": args.vm_user,
        "ssh_password": args.vm_password
    }
    environment.env_add_domain(args.name, vm_info_dict)


def cmd_modify_vm(args):
    vm_info_dict = {
        "name": args.vm_name,
        "src_name": args.vm_src_name,
        "if_name": args.vm_if_name,
        "addr": args.vm_addr,
        "mask": args.vm_mask,
        "gateway": args.vm_gateway,
        "dns": args.vm_dns,
        "ssh_user": args.vm_user,
        "ssh_password": args.vm_password
    }
    environment.env_modify_domain(args.name, vm_info_dict)


def cmd_delete_vm(args):
    environment.env_remove_domain(args.name, args.vm_name)


def cmd_vm_info(args):
    result = environment.env_get_vm_info(args.name, args.vm_name)
    for i, j in result.items():
        print '%s  %s' % (i, j)


def cmd_list(args):
    result = environment.list_env()
    print '\n'.join(result)


def cmd_list_vm(args):
    result = environment.env_get_vm_list(args.name)
    print '\n'.join(result)


def cmd_remove(args):
    environment.remove_env(args.name)


def cmd_vm_init_all(args):
    environment.env_initial(args.name)


def cmd_start(args):
    environment.env_start(args.name)


def cmd_stop(args):
    environment.env_shutdown(args.name)


def cmd_process_ssh_cmd(args):
    environment.env_ssh_cmd(args.name, args.vm_name, args.cmd)


def cmd_ssh_put(args):
    environment.env_ssh_put(args.name, args.vm_name, args.src, args.dst)


def cmd_ssh_get(args):
    environment.env_ssh_get(args.name, args.vm_name, args.src, args.dst)
