# coding:utf-8

# entry of testcase command

import argparse
from erleuchten import vm
from erleuchten.vm import VM


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-vm')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'VM utility')

    p_list = sub_parsers.add_parser('list', help='list domains')
    p_list.add_argument('--status', help='list domain status',
                        choices=['all', 'running', 'stopped'], default='all')
    p_list.set_defaults(func=cmd_list_domain)

    p_list_disk = sub_parsers.add_parser('list-disk', help='list domain disks')
    p_list_disk.add_argument('--name', help='domain name', required=True)
    p_list_disk.set_defaults(func=cmd_list_domain_disk)

    p_undefine = sub_parsers.add_parser('undefine', help='delete domain')
    p_undefine.add_argument('--name', help='domain name', required=True)
    p_undefine.set_defaults(func=cmd_undefine)

    p_poweron = sub_parsers.add_parser('poweron', help='poweron a domain')
    p_poweron.add_argument('--name', help='domain name')
    p_poweron.set_defaults(func=cmd_poweron_domain)

    p_poweroff = sub_parsers.add_parser('poweroff', help='poweroff a domain')
    p_poweroff.add_argument('--name', help='domain name', required=True)
    p_poweroff.add_argument('--force', help="force shutoff domain",
                            action='store_true', default=False)
    p_poweroff.set_defaults(func=cmd_poweroff_domain)

    p_attach = sub_parsers.add_parser('attach', help='attach disk to domain')
    p_attach.add_argument('--name', help='domain name', required=True)
    p_attach.add_argument('--target', help='disk in domain dev name',
                          required=True)
    p_attach.add_argument('--source', help='local disk path', required=True)
    p_attach.add_argument('--disk-format', help='local disk format',
                          dest='disk_format', required=True)
    p_attach.set_defaults(func=cmd_attach)

    p_detach = sub_parsers.add_parser('detach', help='detach domain disk')
    p_detach.add_argument('--name', help='domain name', required=True)
    p_detach.add_argument('--target', help='disk in domain dev name',
                          required=True)
    p_detach.set_defaults(func=cmd_detach)

    p_clone = sub_parsers.add_parser('clone', help='create vm from exist vm')
    p_clone.add_argument('--src-name', help='source vm name', required=True,
                         dest='src_name')
    p_clone.add_argument('--new-name', help='new vm name', required=True,
                         dest='new_name')
    p_clone.set_defaults(func=cmd_clone)

    p_list_interfaces = sub_parsers.add_parser('list-if',
                                               help='list all interfaces of a \
                                               domain')
    p_list_interfaces.add_argument('--domain', help='domain name',
                                   dest='dom_name', required=True)
    p_list_interfaces.set_defaults(func=cmd_list_interfaces)

    p_interface_up = sub_parsers.add_parser('if-connect',
                                            help='bring interface up')
    p_interface_up.add_argument('--domain', help='domain name',
                                dest='dom', required=True)
    p_interface_up.add_argument('--if', help='interface name',
                                dest='interface', required=True)
    p_interface_up.set_defaults(func=cmd_interface_up)

    p_interface_down = sub_parsers.add_parser('if-down',
                                              help='bring interface down')
    p_interface_down.add_argument('--domain', help='domain name',
                                  dest='dom', required=True)
    p_interface_down.add_argument('--if', help='interface name',
                                  dest='interface', required=True)
    p_interface_down.set_defaults(func=cmd_interface_down)

    args = main_parser.parse_args()
    args.func(args)


def cmd_list_domain(args):
    # rtn = vm.list_domains(args.status)
    # print ('\n'.join(rtn))
    print("It's not available right now")


def cmd_list_domain_disk(args):
    # rtn = vm.list_domain_disk(args.name)
    # for i in rtn:
    #     print ('{0}  {1}  {2}'.format(i[0], i[1], i[2]))
    print("It's not available right now")


def cmd_undefine(args):
    # vm.undefine_domain_by_name(args.name)
    print("It's not available right now")


def cmd_poweron_domain(args):
    # vm.poweron_domain_by_name(args.name)
    print("It's not available right now")


def cmd_poweroff_domain(args):
    # if args.force:
    #     vm.destrotarget_listy_domain_by_name(args.name)
    # else:
    #     vm.poweroff_domain_by_name(args.name)
    print("It's not available right now")


def cmd_attach(args):
    # vm.attach_disk(args.name, args.source, args.target,
    #                         args.disk_format)
    print("It's not available right now")


def cmd_detach(args):
    # vm.list_domain_disk(args.name, args.target)
    print("It's not available right now")


def cmd_clone(args):
    # vm.clone_vm_by_domain_name(args.src_name, args.new_name)
    print("It's not available right now")


def cmd_list_interfaces(args):
    # rtn = vm.list_interfaces(args.dom_name)
    # for i in rtn:
    #     print ('{0}  {1}  {2}  {3}'.format(i[0], i[1], i[2], i[3]))
    print("It's not available right now")


def cmd_interface_up(args):
    # vm.interface_up(args.dom, args.interface)
    print("It's not available right now")


def cmd_interface_down(args):
    # vm.interface_down(args.dom, args.interface)
    print("It's not available right now")
