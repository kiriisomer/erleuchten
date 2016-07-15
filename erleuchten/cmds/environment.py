# coding:utf-8

# entry of environment

import argparse
from erleuchten import environment


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-env')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'environment utility')

    p_create = sub_parsers.add_parser('create', help='create a environment')
    p_create.add_argument('--name', help='testcase name', required=True)
    p_create.add_argument('--env_name', help='testcase env name', default=None)
    p_create.set_defaults(func=environment.create)

    parser_b = sub_parsers.add_parser('remove', help='remove a environment')
    parser_b.add_argument('--name', help='testcase name', required=True)
    p_create.set_defaults(func=environment.remove)

    args = main_parser.parse_args()
    args.func(args)
