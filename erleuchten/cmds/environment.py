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

    p_set_vm = sub_parsers.add_parser('define-vm', help='define a vm, '
                                      'will be created later')
    p_set_vm.add_argument('--name', help='environment name', required=True)
    p_set_vm.add_argument('--vm-src-name', help='vm source name',
                          required=True, dest='vm_src_name')
    p_set_vm.add_argument('--vm-name', help='vm name', required=True,
                          dest='vm_name')
    p_set_vm.add_argument('--vm-addr', help='vm address', required=True,
                          dest='vm_addr')
    p_set_vm.add_argument('--vm-mask', help='vm mask', required=True,
                          dest='vm_mask')
    p_set_vm.add_argument('--vm-gateway', help='vm gateway', required=True,
                          dest='vm_gateway')
    p_set_vm.add_argument('--vm-dns', help='vm dns', required=True,
                          dest='vm_dns')
    p_set_vm.add_argument('--vm-user', help='vm ssh user name', required=True,
                          dest='vm_user')
    p_set_vm.add_argument('--vm-password', help='vm ssh user password',
                          required=True, dest='vm_password')
    p_set_vm.set_defaults(func=cmd_define_vm)

    p_set_vm = sub_parsers.add_parser('delete-vm', help='delete environment '
                                      'including vm')
    p_set_vm.add_argument('--name', help='environment name', required=True)
    p_set_vm.add_argument('--vm_name', help='environment name', required=True)
    p_set_vm.set_defaults(func=cmd_delete_vm)

    p_info_vm = sub_parsers.add_parser('vm-info', help='get environment '
                                       'including vm info')
    p_info_vm.add_argument('--name', help='environment name', required=True)
    p_info_vm.add_argument('--vm_name', help='environment name', required=True)
    p_info_vm.set_defaults(func=cmd_vm_info)

    p_list_env = sub_parsers.add_parser('list', help='list all environment')
    p_list_env.set_defaults(func=cmd_list)

    p_list_env_vm = sub_parsers.add_parser('list-vm', help='list environment '
                                           'vm')
    p_list_env_vm.add_argument('--name', help='environment name',
                               required=True)
    p_list_env_vm.add_argument('--vm-name', help='environment name',
                               dest='vm_name', required=True)
    p_list_env_vm.set_defaults(func=cmd_list_vm)

    p_remove = sub_parsers.add_parser('remove', help='remove a environment')
    p_remove.add_argument('--name', help='environment name', required=True)
    p_remove.set_defaults(func=cmd_remove)

    p_remove = sub_parsers.add_parser('start', help='start all environment'
                                      'vm')
    p_remove.add_argument('--name', help='environment name', required=True)
    p_remove.set_defaults(func=cmd_start)

    p_remove = sub_parsers.add_parser('stop', help='stop all environment'
                                      'vm')
    p_remove.add_argument('--name', help='environment name', required=True)
    p_remove.set_defaults(func=cmd_stop)

    args = main_parser.parse_args()
    args.func(args)


def cmd_create(args):
    environment.create_env(args.name)


def cmd_define_vm(args):
    vm_info_dict = {
        "name": args.vm_name,
        "src_name": args.vm_src_name,
        "addr": args.vm_addr,
        "mask": args.vm_mask,
        "gateway": args.vm_gateway,
        "dns": args.vm_dns,
        "ssh_user": args.vm_user,
        "ssh_password": args.vm_password
    }
    environment.env_add_domain(args.name, vm_info_dict)


def cmd_delete_vm(args):
    environment.env_remove_domain(args.name, args.vm_name)


def cmd_vm_info(args):
    environment.env_get_vm_info(args.name, args.vm_name)


def cmd_list(args):
    result = environment.list_env()
    print '\n'.join(result)


def cmd_list_vm(args):
    result = environment.env_get_vm_list(args.name)
    print '\n'.join(result)


def cmd_remove(args):
    environment.remove_env(args.name)


def cmd_start(args):
    environment.env_start(args.name)


def cmd_stop(args):
    environment.env_shutdown(args.name)
