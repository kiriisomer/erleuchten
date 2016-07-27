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
    p_create.add_argument('--env_name', help='testcase env name', default=None)
    p_create.set_defaults(func=cmd_create)

    p_set_vm = sub_parsers.add_parser('set-vm', help='set environment '
                                      'including vm info')
    p_set_vm.add_argument('--name', help='environment name', required=True)
    p_set_vm.add_argument('--vm-name', help='vm name', required=True)
    p_set_vm.add_argument('--vm-addr', help='vm address', required=True)
    p_set_vm.add_argument('--vm-mask', help='vm mask', required=True)
    p_set_vm.add_argument('--vm-gateway', help='vm gateway', required=True)
    p_set_vm.add_argument('--vm-dns', help='vm dns', required=True)
    p_set_vm.add_argument('--vm-user', help='vm ssh user name', required=True)
    p_set_vm.add_argument('--vm-password', help='vm ssh user password',
                          required=True)

    p_set_vm.set_defaults(func=cmd_set_vm)

    p_set_vm = sub_parsers.add_parser('delete-vm', help='delete environment '
                                      'including vm')
    p_set_vm.add_argument('--name', help='environment name', required=True)
    p_set_vm.set_defaults(func=cmd_delete_vm)

    p_info_vm = sub_parsers.add_parser('vm-info', help='get environment '
                                       'including vm info')
    p_info_vm.add_argument('--name', help='environment name', required=True)
    p_info_vm.add_argument('--vm_name', help='environment name', required=True)
    p_info_vm.set_defaults(func=cmd_vm_info)

    p_list_env = sub_parsers.add_parser('list', help='list all environment')
    p_list_env.set_defaults(func=cmd_list)

    p_list_env_vm = sub_parsers.add_parser('list-vm', help='list environment '
                                           'vm info')
    p_list_env_vm.add_argument('--name', help='environment name',
                               required=True)
    p_list_env_vm.add_argument('--vm-name', help='environment name',
                               dest='vm_name', required=True)
    p_list_env_vm.set_defaults(func=cmd_list_vm)

    p_remove = sub_parsers.add_parser('remove', help='remove a environment')
    p_remove.add_argument('--name', help='environment name', required=True)
    p_remove.set_defaults(func=cmd_remove)

    args = main_parser.parse_args()
    args.func(args)


def cmd_create(args):
    environment.env_create(args.name)


def cmd_set_vm(args):
    pass


def cmd_delete_vm(args):
    pass


def cmd_vm_info(args):
    pass


def cmd_list(args):
    pass


def cmd_list_vm(args):
    pass


def cmd_remove(args):
    pass
