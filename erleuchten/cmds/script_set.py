# coding:utf-8

# entry of script set command

import argparse
import libvirt
from erleuchten.utils.error import ErleuchtenException
from erleuchten import script


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-script-set')
    sub_parsers = main_parser.add_subparsers(help='erleuchten '
                                             'test script set utility')

    p_create = sub_parsers.add_parser('create', help='create a script set')
    p_create.add_argument('--name', help='script set name', required=True)
    p_create.add_argument('--script-name', dest="script_list", nargs="+",
                          help='include script(s) name with order')
    p_create.set_defaults(func=cmd_create)

    p_set = sub_parsers.add_parser('set-script',
                                   help='set script set including scripts')
    p_set.add_argument('--name', help='script set name', required=True)
    p_set.add_argument('--script-name', dest="script_list", nargs="+",
                       help='include script(s) name with order', required=True)
    p_set.set_defaults(func=cmd_set_script)

    p_remove = sub_parsers.add_parser('remove', help='remove a script set')
    p_remove.add_argument('--name', help='script set name', required=True)
    p_remove.add_argument('--force',
                          help="force remove if it's in a testcase",
                          action='store_true', default=False)
    p_remove.set_defaults(func=cmd_remove)

    p_run = sub_parsers.add_parser('run', help='run script')
    p_run.add_argument('--name', help='script name', required=True)
    p_run.set_defaults(func=cmd_run)

    p_list = sub_parsers.add_parser('list', help='list all script')
    p_list.set_defaults(func=cmd_list)

    args = main_parser.parse_args()
    try:
        args.func(args)
    except (IOError, TypeError, ValueError, OSError, SystemError,
            IndexError, ErleuchtenException, libvirt.libvirtError), \
            diag:
        retval = str(diag)
        return retval


def cmd_create(args):
    script.create_script_set(args.name, args.script_list)


def cmd_set_script(args):
    script.set_script_set(args.name, args.script_list)


def cmd_remove(args):
    script.remove_script_set(args.name, args.force)


def cmd_run(args):
    result = script.run_script_set(args.name)
    print '\n'.join(result)


def cmd_list(args):
    result = script.list_script_set()
    print '\n'.join(result)
