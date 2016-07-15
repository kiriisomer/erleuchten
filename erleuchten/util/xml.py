# coding:utf-8

# xml utilities
from lxml import etree


class XML(object):
    """环境，测试用例等的配置文件都使用xml"""

    def __init__(self, xml_path=""):
        self.xml_path = xml_path
        self.xml_obj = None
        if xml_path:
            self.open_parser()

    def open_parser(self, xml_path=""):
        if xml_path != "":
            self.xml_path = xml_path
        utf8_parser = etree.XMLParser(encoding='utf-8', strip_cdata=False)
        try:
            self.xml_obj = etree.parse(self.xml_path, parser=utf8_parser)
        except etree.XMLSyntaxError, e:
            log = e.error_log.filter_from_level(etree.ErrorLevels.FATAL)
            entry = log[0]
            if entry.type_name == "ERR_DOCUMENT_EMPTY":
                self.xml_obj = None


class VMXML(XML):
    """对xml文件操作的封装。虚拟机一般都会有一个XML文件"""

    def get_device_path_list(self):
        """get domain device path from xml"""
        s = self.xml_obj.xpath('/domain/devices/disk/source')
        return [x.get('file') for x in s]


class ConfXML(XML):
    """对xml配置文件操作的封装。环境等设置一般都有一个xml文件"""

    def save_parser(self):
        pass
