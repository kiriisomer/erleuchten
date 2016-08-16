# coding:utf-8

# entry of testcase command

import argparse
from erleuchten import testcase


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-testcase')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'testcase utility')

    p_create = sub_parsers.add_parser('create', help='create a testcase')
    p_create.add_argument('--name', help='testcase name', required=True)
    p_create.add_argument('--env-name', help='testcase env name',
                          dest='env_name', default=None)
    p_create.add_argument('--init-scriptset', default=None,
                          dest='init_scriptset',
                          help='init test environmet script set name')
    p_create.add_argument('--test-scriptset', dest="test_scriptset", nargs="+",
                          help='include test scriptset(s) name with order',
                          default=[])
    p_create.set_defaults(func=cmd_create)

    p_modify = sub_parsers.add_parser('modify', help='create a testcase')
    p_modify.add_argument('--name', help='testcase name', required=True)
    p_modify.add_argument('--env-name', help='testcase env name',
                          dest='env_name', default=None)
    p_modify.add_argument('--init-scriptset', default=None,
                          dest='init_scriptset',
                          help='init test environmet script set name')
    p_modify.add_argument('--test-scriptset', dest="test_scriptset", nargs="+",
                          help='include test scriptset(s) name with order',
                          default=[])
    p_modify.set_defaults(func=cmd_modify)

    p_init = sub_parsers.add_parser('init', help='init testcase environment')
    p_init.add_argument('--name', help='testcase name', required=True)
    p_init.set_defaults(func=cmd_init)

    p_start = sub_parsers.add_parser('start', help='start process test')
    p_start.add_argument('--name', help='testcase name', required=True)
    p_start.set_defaults(func=cmd_start)

    p_stop = sub_parsers.add_parser('stop', help='stop test')
    p_stop.add_argument('--name', help='testcase name', required=True)
    p_stop.set_defaults(func=cmd_stop)

    p_remove = sub_parsers.add_parser('remove', help='remove testcase')
    p_remove.add_argument('--name', help='testcase name', required=True)
    p_remove.set_defaults(func=cmd_remove)

    p_list = sub_parsers.add_parser('remove', help='remove testcase')
    p_list.set_defaults(func=cmd_list)

    args = main_parser.parse_args()
    args.func(args)


def cmd_create(args):
    testcase.create(args.name, args.env_name, args.init_scriptset,
                    args.test_scriptset)


def cmd_modify(args):
    testcase.modify(args.name, args.env_name, args.init_scriptset,
                    args.test_scriptset)


def cmd_init(args):
    testcase.init(args.name)


def cmd_start(args):
    testcase.start(args.name)


def cmd_stop(args):
    testcase.stop(args.name)


def cmd_remove(args):
    testcase.remove(args.name)


def cmd_list(args):
    testcase.list_testcase()