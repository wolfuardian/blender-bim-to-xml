import bpy
import xml.etree.ElementTree as Et
from datetime import datetime
import os

os.system('cls')
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


class XmlCreateSettings:
    def __init__(self):
        self.root = None
        self.data_source = None

    @staticmethod
    def factory(system, version, source):
        settings = XmlCreateSettings()
        # Root
        settings.root = Et.Element("Root")
        settings.root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        settings.root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        # DataSource
        settings.data_source = Et.SubElement(settings.root, "DataSource")
        settings.data_source.set("ProductType", system)
        settings.data_source.set("Version", version)
        settings.data_source.set("Source", source)
        return settings


class XmlCreate:
    def __init__(self, xml_create_settings: XmlCreateSettings):
        self.xml_create_settings = xml_create_settings
        self.root = xml_create_settings.root
        self.data_source = xml_create_settings.data_source
        self.collections = {}
        self.ifc_project = {}
        self.ifc_site = {}
        self.ifc_building = {}
        self.ifc_building_storey = {}
        self.xml_building = None
        self.xml_building_storey = {}

    def execute(self):
        self.store_collections()
        self.parse_ifc_collections()
        self.create_xml_building()
        for storey in self.ifc_building_storey.values():
            self.create_xml_building_storey(storey)
        self.export_xml(file)

    def store_collections(self, collection=bpy.context.view_layer.layer_collection):
        self.collections[collection.name] = collection
        for collection in collection.children:
            self.store_collections(collection)

    def parse_ifc_collections(self):
        for collection in self.collections.values():
            if collection.name.startswith("Ifc"):
                context = {
                    "data": collection,
                    "type": collection.name.split("/")[0],
                    "name": collection.name.split("/")[1]
                }
                if collection.name.startswith("IfcProject/"):
                    self.ifc_project = context
                elif collection.name.startswith("IfcSite/"):
                    self.ifc_site = context
                elif collection.name.startswith("IfcBuilding/"):
                    self.ifc_building = context
                elif collection.name.startswith("IfcBuildingStorey/"):
                    # self.ifc_building_storey.append(context)
                    self.ifc_building_storey[context["name"]] = context

    def create_xml_building(self):
        # Building
        self.xml_building = self.create_xml_node(
            parent=self.root,
            type="Building",
            category="0",
            name=self.ifc_building["name"],
            alias=self.ifc_building["name"],
            id="",
            remark="",
            model=self.ifc_building["name"],
            time=self.get_date_time(),
            noted="created"
        )

        collection = bpy.data.collections[self.ifc_building["data"].name]

        # Transform
        for obj in collection.objects:
            if obj.type == "EMPTY":
                if obj.name == collection.name:
                    self.ifc_building["position"] = [
                        obj.matrix_world.to_translation().x.__str__(),
                        obj.matrix_world.to_translation().y.__str__(),
                        obj.matrix_world.to_translation().z.__str__()
                    ]
                    self.ifc_building["rotation"] = [
                        obj.matrix_world.to_euler().x.__str__(),
                        obj.matrix_world.to_euler().y.__str__(),
                        obj.matrix_world.to_euler().z.__str__()
                    ]
                    self.ifc_building["scale"] = [
                        obj.matrix_world.to_scale().x.__str__(),
                        obj.matrix_world.to_scale().y.__str__(),
                        obj.matrix_world.to_scale().z.__str__()
                    ]

        self.create_xml_transform(
            parent=self.xml_building,
            position=self.ifc_building["position"],
            rotation=self.ifc_building["rotation"],
            scale=self.ifc_building["scale"]
        )

    def create_xml_building_storey(self, storey):
        ifc_transform = self.ifc_building_storey[storey["name"]]

        # BuildingStorey
        self.xml_building_storey[storey["name"]] = self.create_xml_node(
            parent=self.xml_building,
            type="BuildingStorey",
            category="0",
            name=storey["name"],
            alias=storey["name"],
            id="",
            remark="",
            model=storey["name"],
            time=self.get_date_time(),
            noted="created"
        )

        collection = bpy.data.collections[storey["data"].name]

        # Transform
        for obj in collection.objects:
            if obj.type == "EMPTY":
                if obj.name == collection.name:
                    bl_matrix = obj.matrix_world
                    self.save_ifc_transform(
                        ifc_transform=ifc_transform,
                        bl_translation=bl_matrix.to_translation(),
                        bl_euler=bl_matrix.to_euler(),
                        bl_scale=bl_matrix.to_scale()
                    )

        self.create_xml_transform(
            parent=self.xml_building_storey[storey["name"]],
            position=ifc_transform["position"],
            rotation=ifc_transform["rotation"],
            scale=ifc_transform["scale"]
        )

    def export_xml(self, path):
        Et.indent(self.root, space=" " * 4)
        Et.ElementTree(self.root).write(path, encoding="utf-8")

    @staticmethod
    def save_ifc_transform(ifc_transform, bl_translation, bl_euler, bl_scale):
        position = [
            bl_translation.x.__str__(),
            bl_translation.y.__str__(),
            bl_translation.z.__str__()
        ]
        rotation = [
            bl_euler.x.__str__(),
            bl_euler.y.__str__(),
            bl_euler.z.__str__()
        ]
        scale = [
            bl_scale.x.__str__(),
            bl_scale.y.__str__(),
            bl_scale.z.__str__()
        ]
        ifc_transform["position"] = position
        ifc_transform["rotation"] = rotation
        ifc_transform["scale"] = scale

    @staticmethod
    def create_xml_node(parent, type, category, name, alias, id, remark, model, time, noted):
        node = Et.SubElement(parent, "Object")
        node.set("type", type)
        node.set("category", category)
        node.set("name", name)
        node.set("alias", alias)
        node.set("id", id)
        node.set("remark", remark)
        node.set("model", model)
        node.set("time", time)
        node.set("noted", noted)
        return node

    @staticmethod
    def create_xml_transform(parent, position, rotation, scale):
        transform = Et.SubElement(parent, "Transform")
        pos = Et.SubElement(transform, "position")
        pos.set("x", position[0])
        pos.set("y", position[1])
        pos.set("z", position[2])
        rot = Et.SubElement(transform, "rotation")
        rot.set("x", rotation[0])
        rot.set("y", rotation[1])
        rot.set("z", rotation[2])
        scl = Et.SubElement(transform, "scale")
        scl.set("x", scale[0])
        scl.set("y", scale[1])
        scl.set("z", scale[2])

    def get_ifc_types_mesh(self):
        pass

    @staticmethod
    def get_date_time():
        dt = datetime.now()
        return dt.strftime("%Y/%m/%d %H:%M")


def main():
    # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    # Pre-Settings
    xml_create_settings = XmlCreateSettings.factory("OCMS2_0", "2023.02.16", "Unity")
    # Create
    xml_create = XmlCreate(xml_create_settings)
    xml_create.execute()
    # print(f"collections: {xml_create.collections}")
    # Analysis collection
    # col_building = select_collection("IfcBuilding/")
    # print(f"col_building: {col_building}")


main()
