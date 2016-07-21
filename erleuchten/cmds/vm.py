# coding:utf-8

# entry of testcase command

import argparse
from erleuchten import environment


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-vm')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'VM utility')

    p_create = sub_parsers.add_parser('create', help='create a vm')
    p_create.add_argument('--name', help='script name', required=True)
    p_create.add_argument('--xml-path', dest="xml_path",
                          help='xml file path', required=True)
    p_create.set_defaults(func=cmd_create_vm)


def cmd_create_vm(args):
    pass
