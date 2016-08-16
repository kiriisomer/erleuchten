# coding:utf-8


import ConfigParser


__all__ = ['get']


PATH_CONFIG_FILE = '/etc/erleuchten.conf'


default_conf = {
    PATH_TESTCASE: '/home/erleuchten/testcase',
    PATH_SCRIPT: '/home/erleuchten/testscript',
    PATH_SCRIPT_SET: '/home/erleuchten/testscriptset',
    PATH_VM_TEMPLATE: '/home/erleuchten/vm_template',
    PATH_VM: '/home/erleuchten/vm',
    PATH_ENVIRONMENT: '/home/erleuchten/environment',
    SHELL_EXECUTOR: '/bin/sh',
}


# 全局配置，初始化后应为｛"section1":{"key1":"val1", ...}, ...｝
_global_config = None


def get(attribute):
    """获取参数"""
    global _global_config
    if _global_config is None:
        _global_config = default_conf
        _global_config.update(load_config(PATH_CONFIG_FILE))
    return _global_config[attribute]


def load_config(file):
    config = ConfigParser.RawConfigParser(dict_type=dict)
    try:
        config.readfp(open(file))
    except IOError:
        # 打不开文件,退出
        return {}
    return config.defaults()
