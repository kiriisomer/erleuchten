# coding:utf-8

# xml utilities
from lxml import etree


class XML(object):
    """环境，测试用例等的配置文件都使用xml"""

    def __init__(self, xml_path=""):
        self.xml_path = xml_path
        self.xml_root_obj = None
        if xml_path:
            self.open_parser()

    def open_parser(self, xml_path=""):
        if xml_path != "":
            self.xml_path = xml_path
        utf8_parser = etree.XMLParser(encoding='utf-8', strip_cdata=False)
        try:
            self.xml_root_obj = etree.parse(self.xml_path, parser=utf8_parser)
        except etree.XMLSyntaxError, e:
            # 检查是不是空文档引起的打开出错
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            entry = log[0]
            if entry.type_name == "ERR_DOCUMENT_EMPTY":
                self.xml_root_obj = None
        except IOError:
            # 无法打开文件
            self.xml_root_obj = None

    def new_parser(self):
        """创建一个xml root对象，以往里面读写配置"""
        self.xml_root_obj = etree.Element("erleuchten")

    def write_xml_conf(self, path=None):
        """将xml root对象写入指定文件"""
        if path is None:
            path = self.xml_path
        with open(path, 'w+') as fp:
            fp.write('''<?xml version="1.0" encoding="UTF-8"?>''')
            fp.write('\n')
            fp.write(etree.tostring(self.xml_root_obj, encoding='utf-8',
                                    with_tail=True))


class VMXML(XML):
    """对xml文件操作的封装。虚拟机一般都会有一个XML文件"""

    def get_device_path_list(self):
        """get domain device path from xml"""
        s = self.xml_root_obj.xpath('/domain/devices/disk/source')
        return [x.get('file') for x in s]


class ScriptConf(XML):
    """对Script类的xml配置文件操作的封装。"""

    def __init__(self, xml_path, name):
        super(ScriptConf, self).__init__(xml_path)
        self.name = name

    def get_name(self):
        s = self.xml_root_obj.xpath(
            '/erleuchten/script[@name="%s"]' % self.name)
        try:
            return s[0].get("name")
        except:
            return None

    def save_config(self, conf_dict, write_file=True):
        """将配置保存起来"""
        # 没有root则新建一个
        if self.xml_root_obj is None:
            root = etree.Element("erleuchten")
        else:
            root = self.xml_root_obj

        # 没有script则新建一个
        s = self.xml_root_obj.xpath(
            '/erleuchten/script[@name="%s"]' % self.name)
        if len(s) == 0:
            s = etree.SubElement(root, "script")
            s.set('name', self.name)

        for i, j in conf_dict.items():
            s.set(i, j)

        self.xml_root_obj = root
        if write_file:
            self.write_xml_conf()

    def load_config(self):
        """读取配置，返回一个字典"""
        self.open_parser()
        if self.xml_root_obj is None:
            return {}

        s = self.xml_root_obj.xpath(
            '/erleuchten/script[@name="%s"]' % self.name)
        conf_dict = {}
        conf_dict["script_name"] = s[0].get("script_name")
        conf_dict["pid"] = s[0].get("pid")
        conf_dict["exceed_time"] = s[0].get("exceed_time")
        conf_dict["status"] = s[0].get("status")
        return conf_dict

    def get_script_path(self):
        s = self.xml_root_obj.xpath(
            '/erleuchten/script[@name="%s"]' % self.name)
        try:
            return s[0].get("script_name")
        except:
            return None


class ScriptSetConf(XML):
    """对Script类的xml配置文件操作的封装。"""

    def __init__(self, xml_path, name):
        super(ScriptSetConf, self).__init__(xml_path)
        self.name = name

    def get_name(self):
        s = self.xml_root_obj.xpath(
            '/erleuchten/scriptset[@name="%s"]' % self.name)
        try:
            return s[0].get("name")
        except:
            return None

    def save_config(self, conf_dict, write_file=True):
        """将配置保存起来"""
        # 没有root则新建一个
        if self.xml_root_obj is None:
            root = etree.Element("erleuchten")
        else:
            root = self.xml_root_obj

        # 没有script则新建一个
        s = self.xml_root_obj.xpath(
            '/erleuchten/scriptset[@name="%s"]' % self.name)
        if len(s) == 0:
            s = etree.SubElement(root, "script")
            s.set('name', self.name)

        for i, j in conf_dict.items():
            s.set(i, j)

        self.xml_root_obj = root
        if write_file:
            self.write_xml_conf()

    def load_config(self):
        """读取配置，返回一个字典"""
        self.open_parser()
        if self.xml_root_obj is None:
            return {}

        s = self.xml_root_obj.xpath(
            '/erleuchten/scriptset[@name="%s"]' % self.name)
        conf_dict = {}
        conf_dict["script_name_list"] = s[0].get("script_name_list")
        conf_dict["return_code_list"] = s[0].get("return_code_list")
        conf_dict["status"] = s[0].get("status")
        return conf_dict
