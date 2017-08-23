# coding:utf-8

# entry of vm img operation

import argparse
from erleuchten.utils import img


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-img')
    sub_parsers = main_parser.add_subparsers(help='erleuchten img  utility')

    p_ls = sub_parsers.add_parser('ls', help='List the files in directory')
    p_ls.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_ls.add_argument(
        '--dir', help='directory that u want to list files', required=True)
    p_ls.set_defaults(func=cmd_ls)

    p_new = sub_parsers.add_parser('new', help='create a new file')
    p_new.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_new.add_argument('--file', help='path of the new file', required=True)
    p_new.set_defaults(func=cmd_new)

    p_remove = sub_parsers.add_parser('remove', help='remove a file')
    p_remove.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_remove.add_argument(
        '--file', help='path of the file u want to remove', required=True)
    p_remove.set_defaults(func=cmd_remove)

    p_write = sub_parsers.add_parser(
        'write', help='write content to the file(overwrite the old content)')
    p_write.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_write.add_argument(
        '--file', help='path of the file u want to write', required=True)
    p_write.add_argument(
        '--content', help='content u want to write to the file', required=True)
    p_write.set_defaults(func=cmd_write)

    p_writeappend = sub_parsers.add_parser(
        'write_append', help='''
         write content to the file
        (not overwrite the old content,appends content to the end of file)
        ''')
    p_writeappend.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_writeappend.add_argument(
        '--file', help='path of the file u want to writeappend', required=True)
    p_writeappend.add_argument(
        '--content',
        help='content u want to writeappend to the file', required=True)
    p_writeappend.set_defaults(func=cmd_write_append)

    p_find = sub_parsers.add_parser('find', help='find a file')
    p_find.add_argument(
        '--disk',
        help='disk path for your function', required=True)
    p_find.add_argument(
        '--dir', help='directory that u want to find file', required=True)
    p_find.set_defaults(func=cmd_find)

    p_cat = sub_parsers.add_parser('cat', help='show the content of the file')
    p_cat.add_argument(
        '--disk',
        help='disk path for your function', required=True)
    p_cat.add_argument(
        '--file',
        help='path of the file u want to show its content', required=True)
    p_cat.set_defaults(func=cmd_cat)

    p_copyout = sub_parsers.add_parser(
        'download', help='''
         copies remote files or directories recursively
         out of the disk image
        ''')
    p_copyout.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_copyout.add_argument(
        '--source',
        help='path of remotefilename that u want to download', required=True)
    p_copyout.add_argument(
        '--target',
        help='path of filename that u want to download to', required=True)
    p_copyout.set_defaults(func=cmd_download)

    p_copyin = sub_parsers.add_parser(
        'upload',
        help='copies local files/directories recursively into the disk image')
    p_copyin.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_copyin.add_argument(
        '--source',
        help='path of filename that u want to upload', required=True)
    p_copyin.add_argument(
        '--target',
        help='path of remotefilename that u want to upload to', required=True)
    p_copyin.set_defaults(func=cmd_upload)

    p_modifyifcfg = sub_parsers.add_parser(
        'ifcfg', help='modify vm network configuration')
    p_modifyifcfg.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_modifyifcfg.add_argument(
        '--srcifcfg', help='vm network configuration path', required=True)
    p_modifyifcfg.add_argument('--ip', help='new IPADDR', required=True)
    p_modifyifcfg.add_argument('--mask', help='new netmask')
    p_modifyifcfg.add_argument('--gateway', help='new gateway')
    p_modifyifcfg.add_argument('--dns', help='new dns')
    p_modifyifcfg.set_defaults(func=cmd_modifyifcfg)

    p_end = sub_parsers.add_parser(
        'shutdown', help='umount all filesystems, shutdown vm, close guestfs')
    p_end.add_argument(
        '--disk', help='disk path for your function', required=True)
    p_end.set_defaults(func=cmd_shutdown_vm)

    args = main_parser.parse_args()
    args.func(args)


def cmd_ls(args):
    print img.ls(args.disk, args.dir)


def cmd_new(args):
    img.new(args.disk, args.file)


def cmd_remove(args):
    img.remove(args.disk, args.file)


def cmd_write(args):
    img.write(args.disk, args.file, args.content)


def cmd_write_append(args):
    img.write_append(args.disk, args.file, args.content)


def cmd_find(args):
    print img.find(args.disk, args.dir)


def cmd_cat(args):
    print img.cat(args.disk, args.file)


def cmd_download(args):
    img.download(args.disk, args.source, args.target)


def cmd_upload(args):
    img.upload(args.disk, args.source, args.target)


def cmd_modifyifcfg(args):
    img.modifyifcfg(
        args.disk, args.srcifcfg, args.ip)


def cmd_shutdown_vm(args):
    img.shutdown_vm(args.disk)
