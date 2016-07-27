# coding:utf-8

# entry of script set command

import argparse
from erleuchten.util import remote


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-remote')
    sub_parsers = main_parser.add_subparsers(help='erleuchten remote '
                                             'utility')

    p_upload = sub_parsers.add_parser('put', help='upload local file '
                                      'to remote host')
    p_upload.add_argument('--addr', help='remote host address', required=True)
    p_upload.add_argument('--user', help='remote host user', required=True)
    p_upload.add_argument('--pswd', help='remote host user password',
                          required=True)
    p_upload.add_argument('--src', help='local upload file path',
                          required=True)
    p_upload.add_argument('--dest', help='remote file destnation path',
                          required=True)
    p_upload.set_defaults(func=cmd_upload)

    p_upload = sub_parsers.add_parser('get', help='download remote host file '
                                      'to local')
    p_upload.add_argument('--addr', help='remote host address', required=True)
    p_upload.add_argument('--user', help='remote host user', required=True)
    p_upload.add_argument('--pswd', help='remote host user password',
                          required=True)
    p_upload.add_argument('--src', help='remote file path', required=True)
    p_upload.add_argument('--dest', help='local file save path',
                          required=True)
    p_upload.set_defaults(func=cmd_download)

    p_exec = sub_parsers.add_parser('execute', help='execute a command '
                                    'on remote host')
    p_exec.add_argument('--addr', help='remote host address', required=True)
    p_exec.add_argument('--user', help='remote host user', required=True)
    p_exec.add_argument('--pswd', help='remote host user password',
                        required=True)
    p_exec.add_argument('--cmd', help='process command', required=True)
    p_exec.set_defaults(func=cmd_execute)

    args = main_parser.parse_args()
    args.func(args)


def cmd_execute(args):
    print remote.fabric_command(args.addr, args.user, args.pswd, args.cmd)


def cmd_upload(args):
    print remote.fabric_put(args.addr, args.user, args.pswd,
                            args.src, args.dest)


def cmd_download(args):
    print remote.fabric_get(args.addr, args.user, args.pswd,
                            args.src, args.dest)
