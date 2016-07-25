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

    p_poweron = sub_parsers.add_parser('poweron', help='poweron a domain')
    group = p_poweron.add_mutually_exclusive_group(required=True)
    group.add_argument('--id', help='domain id', type=int)
    group.add_argument('--name', help='domain name')
    p_poweron.set_defaults(func=cmd_poweron_domain)

    p_poweroff = sub_parsers.add_parser('poweroff', help='poweroff a domain')
    p_poweroff.add_argument('--name', help='domain name', required=True)
    p_poweroff.add_argument('--force', help="force shutoff domain",
                            action='store_true', default=False)
    p_poweroff.set_defaults(func=cmd_poweroff_domain)

    args = main_parser.parse_args()
    args.func(args)


def cmd_poweron_domain(args):
    if args.id is not None:
        environment.poweron_domain_by_id(args.id)
    else:
        environment.poweron_domain_by_name(args.name)


def cmd_poweroff_domain(args):
    if args.force:
        environment.destroy_domain_by_name(args.name)
    else:
        environment.poweroff_domain_by_name(args.name)


def cmd_list_domain(args):
    environment.list_domains(args.status)


def cmd_list_domain_disk(args):
    environment.list_domain_disk(args.name)

