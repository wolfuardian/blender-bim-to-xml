import bpy
import xml.etree.ElementTree as Et

output = "C:\\Users\\eos\\PycharmProjects\\blender-bim-to-xml\\tests\\ExportXML"
filename = "UnitTest_ExportXML_20230425_001.xml"

file = output + "\\" + filename


class XmlBuilder:
    def __init__(self):
        self.root = None
        self.data_source = None

    @staticmethod
    def factory(system, version, source):
        builder = XmlBuilder()
        # Root
        builder.root = Et.Element("Root")
        builder.add_attribute(builder.root, "xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        builder.add_attribute(builder.root, "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        # DataSource
        builder.data_source = Et.SubElement(builder.root, "DataSource")
        builder.add_attribute(builder.data_source, "ProductType", system)
        builder.add_attribute(builder.data_source, "Version", version)
        builder.add_attribute(builder.data_source, "Source", source)
        return builder

    @staticmethod
    def add_attribute(node: Et.Element, name, value):
        node.set(name, value)

    def write(self, path):
        Et.indent(self.root, space=" " * 4)
        Et.ElementTree(self.root).write(path, encoding="utf-8")


def main():
    xb = XmlBuilder()
    xb = xb.factory("OCMS2_0", "2023.02.16", "Unity")
    xb.write(file)


main()
