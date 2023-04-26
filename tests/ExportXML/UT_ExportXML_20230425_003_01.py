import bpy
import xml.etree.ElementTree as Et

output = "C:\\Users\\eos\\PycharmProjects\\blender-bim-to-xml\\tests\\ExportXML"
filename = "UnitTest_ExportXML_20230425_001.xml"

file = output + "\\" + filename


def select_collection(name):
    def recursive_search(collection):
        for collection in collection.children:
            if name in collection.name:
                bpy.context.view_layer.active_layer_collection = collection
            recursive_search(collection)
        return bpy.context.view_layer.active_layer_collection
    return recursive_search(bpy.context.view_layer.layer_collection)


class XmlBuilder:
    def __init__(self):
        self.root = None
        self.data_source = None

    @staticmethod
    def factory(system, version, source):
        builder = XmlBuilder()
        # Root
        builder.root = Et.Element("Root")
        builder.root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        builder.root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        # DataSource
        builder.data_source = Et.SubElement(builder.root, "DataSource")
        builder.data_source.set("ProductType", system)
        builder.data_source.set("Version", version)
        builder.data_source.set("Source", source)
        # Building
        builder.building = Et.SubElement(builder.root, "Object")
        builder.building.set("type", "Building")
        builder.building.set("category", "")
        builder.building.set("name", "")
        builder.building.set("alias", "")
        builder.building.set("model", "")
        builder.building.set("time", "")
        builder.building.set("noted", "")
        return builder

    def write(self, path):
        Et.indent(self.root, space=" " * 4)
        Et.ElementTree(self.root).write(path, encoding="utf-8")


def main():
    print("\n\n\n")
    # Create XML
    xml_builder = XmlBuilder()
    xml_builder = xml_builder.factory("OCMS2_0", "2023.02.16", "Unity")
    # Analysis collection
    col_building = select_collection("IfcProject/")
    col_building = select_collection("IfcBuilding/")
    print(f"col_building: {col_building}")

    xml_builder.write(file)


main()
