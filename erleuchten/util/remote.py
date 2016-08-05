# coding: utf8

from fabric import api


def _run_cmd(cmd):
    """运行命令"""
    out = api.run(cmd)
    return out.return_code


def _put_file(local_src, remote_dst):
    """上传文件"""
    api.put(local_src, remote_dst)


def _get_file(remote_src, local_dst):
    """获取文件"""
    api.get(remote_src, local_dst)


def fabric_command(addr, user, password, cmd):
    host = '{user}@{addr}:22'.format(user=user, addr=addr)
    api.env.hosts = [host]
    api.env.passwords = {host: password}

    result = api.execute(_run_cmd, cmd=cmd)
    return result.get(host, 3)


def fabric_put(addr, user, password, src, dst):
    host = '{user}@{addr}:22'.format(user=user, addr=addr)
    api.env.hosts = [host]
    api.env.passwords = {host: password}

    result = api.execute(_put_file, local_src=src, remote_dst=dst)
    return result.get(host, 3)


def fabric_get(addr, user, password, src, dst):
    host = '{user}@{addr}:22'.format(user=user, addr=addr)
    api.env.hosts = [host]
    api.env.passwords = {host: password}

    result = api.execute(_get_file, remote_src=src, local_dst=dst)
    return result.get(host, 3)
