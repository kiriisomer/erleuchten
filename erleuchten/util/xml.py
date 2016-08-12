# coding:utf-8

# xml utilities
from lxml import etree
from erleuchten.util.util import ramdom_mac_addr, create_file_path, \
    make_file_lock
from erleuchten.util.error import ErleuchtenException
from erleuchten.util.error import Errno


class XML(object):
    """环境，测试用例等的配置文件都使用xml"""

    def __init__(self, xml_path=""):
        """xml_path可以是文件路径，也可以是stringIO对象"""
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

    def get_xml_str(self):
        return etree.tostring(self.xml_root_obj, encoding='utf-8')

    def write_xml_conf(self, path=None):
        """将xml root对象写入指定文件"""
        if path is None:
            path = self.xml_path
        create_file_path(self.xml_path)
        with open(path, 'w+') as fp:
            with make_file_lock(fp):
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

    def get_all_disk_device(self):
        """获取设备 路径名与文件路径"""
        s = self.xml_root_obj.xpath('/domain/devices/disk[@device="disk"]')
        rtn_list = []
        for x in s:
            d = (x.xpath('target')[0].get("dev"))
            f = (x.xpath('source')[0].get("file"))
            t = (x.xpath('driver')[0].get("type"))
            rtn_list.append([d, f, t])

        return rtn_list

    def get_disk_device_info_by_dev(self, dev_name):
        """通过设备路径名获取磁盘文件路径与磁盘文件格式"""
        s = self.xml_root_obj.xpath('/domain/devices/disk[@device="disk"]'
                                    '/target[@dev="{dev}"]'
                                    ''.format(dev=dev_name))
        if len(s) != 1:
            raise ErleuchtenException(Errno.ERRNO_XML_CANNOT_FIND_DISK)
        x = s[0].getparent()
        d = (x.xpath('target')[0].get("dev"))
        f = (x.xpath('source')[0].get("file"))
        t = (x.xpath('driver')[0].get("type"))
        return (d, f, t)

    def modify_vm_name(self, new_name):
        s = self.xml_root_obj.xpath('/domain/name')
        if len(s) != 1:
            raise ErleuchtenException(Errno.ERRNO_XML_CANNOT_FIND_DOMAIN_NAME)
        s[0].text = new_name

    def modify_vm_uuid(self, new_uuid):
        s = self.xml_root_obj.xpath('/domain/uuid')
        if len(s) != 1:
            raise ErleuchtenException(Errno.ERRNO_XML_CANNOT_FIND_DOMAIN_UUID)
        if new_uuid == s[0].text:
            raise ErleuchtenException(Errno.ERRNO_XML_DONAMIN_UUID_CONFLICT)
        s[0].text = new_uuid

    def modify_disk_file_path(self, dev_name, new_file_path):
        s = self.xml_root_obj.xpath('/domain/devices/disk[@device="disk"]'
                                    '/target[@dev="{dev}"]'
                                    ''.format(dev=dev_name))
        if len(s) != 1:
            raise ErleuchtenException(Errno.ERRNO_XML_CANNOT_FIND_DISK)
        x = s[0].getparent().xpath('source')[0]
        x.set("file", new_file_path)

    def randomize_interface_mac(self):
        """遍历interface mac元素，修改addr"""
        s = self.xml_root_obj.xpath('/domain/devices/interface/mac')
        for i in s:
            i.set("address", ramdom_mac_addr())


class ScriptConf(XML):
    """对Script类的xml配置文件操作的封装。"""

    def __init__(self, xml_path, name):
        super(ScriptConf, self).__init__(xml_path)
        self.name = name

    def get_name(self):
        if self.xml_root_obj is None:
            return None
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
        result = root.xpath('/erleuchten/script[@name="%s"]' % self.name)
        if len(result) == 0:
            s = etree.SubElement(root, "script")
            s.set('name', self.name)
        else:
            s = result[0]

        for i, j in conf_dict.items():
            s.set(str(i), str(j))

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
        if self.xml_root_obj is None:
            return None
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
        result = root.xpath(
            '/erleuchten/scriptset[@name="%s"]' % self.name)
        if len(result) == 0:
            set_obj = etree.SubElement(root, "scriptset")
            set_obj.set('name', self.name)
        else:
            set_obj = result[0]

        for i, j in conf_dict.items():
            if i == 'script_name_list':
                # 使用子元素保存script
                for k in set_obj.iterchildren():
                    set_obj.remove(k)
                for m in conf_dict[i]:
                    s = etree.SubElement(set_obj, "script")
                    s.set('name', str(m))
            elif i == 'return_code_list':
                # 使用空格分隔的字符串保存返回代码
                set_obj.set(str(i), ' '.join([str(x) for x in j]))
            else:
                set_obj.set(str(i), str(j))

        self.xml_root_obj = root
        if write_file:
            self.write_xml_conf()

    def load_config(self):
        """读取配置，返回一个字典"""
        self.open_parser()
        if self.xml_root_obj is None:
            return {}

        set_obj = self.xml_root_obj.xpath(
            '/erleuchten/scriptset[@name="%s"]' % self.name)
        conf_dict = {}
        conf_dict["return_code_list"] = [
            x for x in set_obj[0].get("return_code_list").split()]
        conf_dict["status"] = set_obj[0].get("status")

        script_name_list = []
        for s in set_obj[0].xpath('script'):
            script_name_list.append(s.get("name"))
        conf_dict["script_name_list"] = script_name_list

        return conf_dict


class EnvConf(XML):
    """对Script类的xml配置文件操作的封装。"""

    def __init__(self, xml_path, name):
        super(EnvConf, self).__init__(xml_path)
        self.name = name

    def get_name(self):
        if self.xml_root_obj is None:
            return None
        s = self.xml_root_obj.xpath(
            '/erleuchten/env[@name="%s"]' % self.name)
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
        result = root.xpath('/erleuchten/env[@name="%s"]' % self.name)
        if len(result) == 0:
            set_obj = etree.SubElement(root, "env")
            set_obj.set('name', self.name)
        else:
            set_obj = result[0]

        for i, j in conf_dict.items():
            if i == 'vm_info_list':
                # 使用子元素保存vm信息
                for vm in set_obj.iterchildren():
                    set_obj.remove(vm)
                for vm in conf_dict[i]:
                    r = etree.SubElement(set_obj, "vm")
                    r.set('name', str(vm['name']))
                    r.set('src_name', str(vm['src_name']))
                    r.set('if_name', str(vm['if_name']))
                    r.set('addr', str(vm['addr']))
                    r.set('mask', str(vm['mask']))
                    r.set('gateway', str(vm['gateway']))
                    r.set('dns', str(vm['dns']))
                    r.set('ssh_user', str(vm['ssh_user']))
                    r.set('ssh_password', str(vm['ssh_password']))
            else:
                set_obj.set(str(i), str(j))

        self.xml_root_obj = root
        if write_file:
            self.write_xml_conf()

    def load_config(self):
        """读取配置，返回一个字典"""
        self.open_parser()
        if self.xml_root_obj is None:
            return {}

        set_obj = self.xml_root_obj.xpath(
            '/erleuchten/env[@name="%s"]' % self.name)
        conf_dict = {}
        conf_dict["status"] = set_obj[0].get("status")

        vm_info_list = []
        for s in set_obj[0].xpath('vm'):
            vm = {}
            vm['name'] = s.get('name')
            vm['src_name'] = s.get('src_name')
            vm['if_name'] = s.get('if_name')
            vm['addr'] = s.get('addr')
            vm['mask'] = s.get('mask')
            vm['gateway'] = s.get('gateway')
            vm['dns'] = s.get('dns')
            vm['ssh_user'] = s.get('ssh_user')
            vm['ssh_password'] = s.get('ssh_password')
            vm_info_list.append(vm)

        conf_dict["vm_info_list"] = vm_info_list
        return conf_dict

    def list_include_vm_name(self):
        """列出包含的虚拟机的名字"""
        s = self.xml_root_obj.xpath(
            '/erleuchten/env[@name="%s"]/vm' % self.name)

        return [x.get("name") for x in s]
