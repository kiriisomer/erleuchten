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
    p_create.add_argument('--env_name', help='testcase env name', default=None)
    p_create.set_defaults(func=testcase.create)

    parser_b = sub_parsers.add_parser('remove', help='remove a testcase')
    parser_b.add_argument('--name', help='testcase name', required=True)
    p_create.set_defaults(func=testcase.remove)

    args = main_parser.parse_args()
    args.func(args)
