# coding:utf-8

# xml utilities
from lxml import etree


class VMXML(object):
    """对xml文件操作的封装。虚拟机都会有一个XML文件"""

    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.xml_obj = None
        self.open_parser()

    def open_parser(self):
        utf8_parser = etree.XMLParser(encoding='utf-8', strip_cdata=False)
        self.xml_obj = etree.parse(self.xml_path, parser=utf8_parser)

    def get_device_path_list(self):
        """get domain device path from xml"""
        s = self.xml_obj.xpath('/domain/devices/disk/source')
        return [x.get('file') for x in s]
