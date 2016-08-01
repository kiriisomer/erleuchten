# coding:utf-8

# entry of script set command

import argparse
from erleuchten import script


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-script')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'test script utility')

    p_create = sub_parsers.add_parser('create', help='create a script')
    p_create.add_argument('--name', help='script name', required=True)
    p_create.add_argument('--script-path', dest="script_path",
                          help='script storage path', required=True)
    p_create.set_defaults(func=cmd_create)

    p_remove = sub_parsers.add_parser('remove', help='remove a script')
    p_remove.add_argument('--name', help='script name', required=True)
    p_remove.add_argument('--force',
                          help="force remove if it's in a script set",
                          action='store_true', default=False)
    p_remove.set_defaults(func=cmd_remove)

    p_run = sub_parsers.add_parser('run', help='run script')
    p_run.add_argument('--name', help='script name', required=True)
    p_run.set_defaults(func=cmd_run)

    p_list = sub_parsers.add_parser('list', help='list all script')
    p_list.set_defaults(func=cmd_list)

    args = main_parser.parse_args()
    args.func(args)


def cmd_create(args):
    script.create_script(args.name, args.script_path)


def cmd_remove(args):
    script.remove_script(args.name)


def cmd_run(args):
    script.run_script(args.name)


def cmd_list(args):
    result = script.list_script()
    print '\n'.join(result)
