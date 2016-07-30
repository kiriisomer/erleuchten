# coding:utf-8

# entry of vm img operation

import argparse
from erleuchten.util import img


def main():
    main_parser = argparse.ArgumentParser(prog='erleuchten-img')
    sub_parsers = main_parser.add_subparsers(help='erleuchten img utility')

    p_ls = sub_parsers.add_parser('ls', help='List the files in directory ')
    p_ls.add_argument('--diskpath', help='disk path for your function')
    p_ls.add_argument(
        '--directory', help='directory that u want to list files')
    p_ls.set_defaults(func=cmd_ls)

    p_new = sub_parsers.add_parser('new', help='create a new file')
    p_new.add_argument('--diskpath', help='disk path for your function')
    p_new.add_argument('--filepath', help='path of the new file')
    p_new.set_defaults(func=cmd_new)

    p_remove = sub_parsers.add_parser('remove', help='remove a file')
    p_remove.add_argument('--diskpath', help='disk path for your function')
    p_remove.add_argument(
        '--filepath', help='path of the file u want to remove')
    p_remove.set_defaults(func=cmd_remove)

    p_write = sub_parsers.add_parser(
        'write', help='write content to the file(overwrite the old content)')
    p_write.add_argument('--diskpath', help='disk path for your function')
    p_write.add_argument('--filepath', help='path of the file u want to write')
    p_write.add_argument(
        '--content', help='content u want to write to the file')
    p_write.set_defaults(func=cmd_write)

    p_writeappend = sub_parsers.add_parser(
        'write_append', help='''
         write content to the file
        (not overwrite the old content,appends content to the end of file)
        ''')
    p_writeappend.add_argument(
        '--diskpath', help='disk path for your function')
    p_writeappend.add_argument(
        '--filepath', help='path of the file u want to writeappend')
    p_writeappend.add_argument(
        '--content', help='content u want to writeappend to the file')
    p_writeappend.set_defaults(func=cmd_write_append)

    p_find = sub_parsers.add_parser('find', help='find a file')
    p_find.add_argument('--diskpath', help='disk path for your function')
    p_find.add_argument(
        '--directory', help='directory that u want to find file')
    p_find.set_defaults(func=cmd_find)

    p_cat = sub_parsers.add_parser('cat', help='show the content of the file')
    p_cat.add_argument('--diskpath', help='disk path for your function')
    p_cat.add_argument(
        '--filepath', help='path of the file u want to show its content')
    p_cat.set_defaults(func=cmd_cat)

    p_copyout = sub_parsers.add_parser(
        'download', help='''
         copies remote files or directories recursively
         out of the disk image
        ''')
    p_copyout.add_argument('--diskpath', help='disk path for your function')
    p_copyout.add_argument(
        '--sourcepath', help='path of remotefilename that u want to download')
    p_copyout.add_argument(
        '--targetpath', help='path of filename that u want to download to')
    p_copyout.set_defaults(func=cmd_download)

    p_copyin = sub_parsers.add_parser('upload', help='copy local file or'
                                      'directory into the disk image')
    p_copyin.add_argument('--diskpath', help='disk path for your function')
    p_copyin.add_argument(
        '--sourcepath', help='path of filename that u want to upload')
    p_copyin.add_argument(
        '--targetpath', help='path of remotefilename that u want to upload to')
    p_copyin.set_defaults(func=cmd_upload)

    p_modifyifcfg = sub_parsers.add_parser(
        'ifcfg', help='modify vm network configuration')
    p_modifyifcfg.add_argument(
        '--diskpath', help='disk path for your function')
    p_modifyifcfg.add_argument(
        '--oldifcfg', help='vm network configuration path')
    p_modifyifcfg.add_argument('--tmppath', help='oldifcfg tmp')
    p_modifyifcfg.add_argument(
        '--newifcfg', help='new network configuration path')
    p_modifyifcfg.add_argument('--ip', help='new IPADDR')
    p_modifyifcfg.set_defaults(func=cmd_modifyifcfg)

    p_end = sub_parsers.add_parser(
        'shutdown', help='umount all filesystems, shutdown vm, close guestfs')
    p_end.add_argument('--diskpath', help='disk path for your function')
    p_end.set_defaults(func=cmd_shutdown_vm)

    args = main_parser.parse_args()
    args.func(args)


def cmd_ls(args):
    img.ls(args.diskpath, args.directory)


def cmd_new(args):
    img.new(args.diskpath, args.filepath)


def cmd_remove(args):
    img.remove(args.diskpath, args.filepath)


def cmd_write(args):
    img.write(args.diskpath, args.filepath, args.content)


def cmd_write_append(args):
    img.write_append(args.diskpath, args.filepath, args.content)


def cmd_find(args):
    print img.find(args.diskpath, args.directory)


def cmd_cat(args):
    print img.cat(args.diskpath, args.filepath)


def cmd_download(args):
    img.download(args.diskpath, args.sourcepath, args.targetpath)


def cmd_upload(args):
    img.upload(args.diskpath, args.sourcepath, args.targetpath)


def cmd_modifyifcfg(args):
    img.modifyifcfg(
        args.diskpath, args.oldifcfg, args.tmppath, args.newifcfg, args.ip)


def cmd_shutdown_vm(args):
    img.shutdown_vm(args.diskpath)

