# coding:utf-8

# entry of testcase command

import argparse
from erleuchten import environment


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

    args = main_parser.parse_args()
    args.func(args)


def cmd_undefine(args):
    environment.undefine_domain_by_name(args.name)


def cmd_poweron_domain(args):
    environment.poweron_domain_by_name(args.name)


def cmd_poweroff_domain(args):
    if args.force:
        environment.destroy_domain_by_name(args.name)
    else:
        environment.poweroff_domain_by_name(args.name)


def cmd_list_domain(args):
    rtn = environment.list_domains(args.status)
    print('\n'.join(rtn))


def cmd_list_domain_disk(args):
    rtn = environment.list_domain_disk(args.name)
    for i in rtn:
        print '{0} {1} {2}'.format(i[0], i[1], i[2])


def cmd_attach(args):
    environment.attach_disk(args.name, args.source, args.target,
                            args.disk_format)


def cmd_detach(args):
    environment.list_domain_disk(args.name, args.target)


def cmd_clone(args):
    # environment.list_domain_disk(args.name)
    pass
