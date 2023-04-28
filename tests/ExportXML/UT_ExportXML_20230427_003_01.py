import bpy
import xml.etree.ElementTree as Et
from datetime import datetime
import os

os.system('cls')
output = "C:\\Users\\eos\\PycharmProjects\\blender-bim-to-xml\\tests\\ExportXML"
filename = "UnitTest_ExportXML_20230425_001.xml"

file = output + "\\" + filename


class XMLCreateSettings:
    def __init__(self):
        self.root = None
        self.tree = None
        self.data_source = None

    @staticmethod
    def factory(system, version, source):
        settings = XMLCreateSettings()
        # Root
        settings.root = Et.Element("Root")
        settings.root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        settings.root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        # Tree
        settings.tree = Et.ElementTree(settings.root)
        # DataSource
        settings.data_source = Et.SubElement(settings.root, "DataSource")
        settings.data_source.set("ProductType", system)
        settings.data_source.set("Version", version)
        settings.data_source.set("Source", source)
        return settings


class XMLCreate:
    def __init__(self, xml_create_settings: XMLCreateSettings):
        self.xml_create_settings = xml_create_settings
        self.root = xml_create_settings.root
        self.tree = xml_create_settings.tree
        self.data_source = xml_create_settings.data_source
        self.bl_op = BlenderOperator()
        self.bl_col_root = self.bl_op.get_collection_by_name("IfcProject/")
        self.bl_obj_root = self.bl_op.add_object("Root")
        self.bl_op.move_to_collection(self.bl_obj_root, self.bl_col_root)
        # self.bl_et = BlenderElementTree(self.bl_op.add_object("Root"))

        self.collections = {}
        self.ifc_project = {}
        self.ifc_site = {}
        self.ifc_building = {}
        self.ifc_building_storey = {}
        self.xml_building = None
        self.xml_building_storey = {}
        self.bl_objects = set()
        self.elements = {}

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
                content = {
                    "data": collection.name,
                    "head": collection.name.split("/")[0],
                    "name": collection.name.split("/")[1]
                }
                if collection.name.startswith("IfcProject/"):
                    self.ifc_project = content
                elif collection.name.startswith("IfcSite/"):
                    self.ifc_site = content
                elif collection.name.startswith("IfcBuilding/"):
                    self.ifc_building = content
                elif collection.name.startswith("IfcBuildingStorey/"):
                    # self.ifc_building_storey.append(content)
                    self.ifc_building_storey[content["name"]] = content

    def create_xml_building(self):
        parent, parent_path = self.get_elements_with_paths(self.root)[-1]
        print(f"[create_xml_building] parent_path: {parent_path}")

        attributes = {
            "type": "Building",
            "category": "0",
            "name": self.ifc_building["name"],
            "alias": self.ifc_building["name"],
            "id": "",
            "remark": "",
            "model": self.ifc_building["name"],
            "time": self.get_date_time(),
            "noted": "created"
        }

        collection = bpy.data.collections[self.ifc_building["data"]]

        transform = {}

        for obj in collection.objects:
            if obj.type == "EMPTY":
                if obj.name == collection.name:
                    transform["position"] = [
                        obj.matrix_world.to_translation().x.__str__(),
                        obj.matrix_world.to_translation().y.__str__(),
                        obj.matrix_world.to_translation().z.__str__()
                    ]
                    transform["rotation"] = [
                        obj.matrix_world.to_euler().x.__str__(),
                        obj.matrix_world.to_euler().y.__str__(),
                        obj.matrix_world.to_euler().z.__str__()
                    ]
                    transform["scale"] = [
                        obj.matrix_world.to_scale().x.__str__(),
                        obj.matrix_world.to_scale().y.__str__(),
                        obj.matrix_world.to_scale().z.__str__()
                    ]

        content = {
            "bl_object": collection.name,
            "bl_type": type(collection).__name__,
            "ifc_info": self.ifc_building,
            "parent_path": parent_path,
            "this_path": None,
            "attributes": attributes,
            "transform": transform
        }
        # self.xml_building = self.add_element(content)
        # self.bl_objects.add({self.add_element(content): content})
        content = self.add_element(content)
        # element, this_path = self.get_element_with_path(self.root)
        # this, this_path = self.get_elements_with_paths(self.root)[-1]
        # print(f"[create_xml_building] this_path: {this_path}")
        # self.elements[this_path] = this
        # print(f"[create_xml_building] elements: {self.elements}")
        bl_object = self.add_properties(content)
        self.bl_objects.add(bl_object)

    def create_xml_building_storey(self, building_storey):
        parent_bl_object = self.find_bl_object_by_ifc_info("head", "IfcBuilding")
        parent = parent_bl_object["this_path"]

        # parent = self.xml_building

        attributes = {
            "type": "BuildingStorey",
            "category": "0",
            "name": building_storey["name"],
            "alias": building_storey["name"],
            "id": "",
            "remark": "",
            "model": building_storey["name"],
            "time": self.get_date_time(),
            "noted": "created"
        }

        collection = bpy.data.collections[building_storey["data"]]

        transform = {}

        for obj in collection.objects:
            if obj.type == "EMPTY":
                if obj.name == collection.name:
                    transform["position"] = [
                        obj.matrix_world.to_translation().x.__str__(),
                        obj.matrix_world.to_translation().y.__str__(),
                        obj.matrix_world.to_translation().z.__str__()
                    ]
                    transform["rotation"] = [
                        obj.matrix_world.to_euler().x.__str__(),
                        obj.matrix_world.to_euler().y.__str__(),
                        obj.matrix_world.to_euler().z.__str__()
                    ]
                    transform["scale"] = [
                        obj.matrix_world.to_scale().x.__str__(),
                        obj.matrix_world.to_scale().y.__str__(),
                        obj.matrix_world.to_scale().z.__str__()
                    ]

        content = {
            "bl_object": collection.name,
            "bl_type": type(collection).__name__,
            "ifc_info": building_storey,
            "parent_path": parent,
            "this_path": None,
            "attributes": attributes,
            "transform": transform
        }
        # self.xml_building_storey[building_storey["name"]] = self.add_element(content)
        # self.xml_building = self.add_element(content)
        content = self.add_element(content)
        bl_object = self.add_properties(content)
        self.bl_objects.add(bl_object)

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

    @staticmethod
    def get_date_time():
        dt = datetime.now()
        return dt.strftime("%Y/%m/%d %H:%M")

    def iter_with_path(self, node: Et.Element, tag: str = None, root_path: str = 'root') -> any:
        if tag == '*':
            tag = None
        if tag is None or node.tag == tag:
            yield node, root_path
        for child in node:
            current = child.get('name')
            child_path = f'{root_path}/{current}'
            for _child, _child_path in self.iter_with_path(child, tag, root_path=child_path):
                yield _child, _child_path

    def get_elements_with_paths(self, root: Et.Element) -> list:
        element = [(elem, path) for elem, path in self.iter_with_path(root, 'Object')]
        if not element:
            element = [(elem, path) for elem, path in self.iter_with_path(root, 'Root')]
            return element
        return element

    def get_last_element(self, root: Et.Element) -> Et.Element:
        element, path = self.get_elements_with_paths(root)[-1]
        return element

    def get_last_path(self, root: Et.Element) -> str:
        element, path = self.get_elements_with_paths(root)[-1]
        return path

    def add_element(self, content):
        # bl_object = element["bl_object"]
        parent_path = content["parent_path"]
        attributes = content["attributes"]
        transform = content["transform"]

        parent = self.root
        if self.elements.keys():
            parent = self.elements[parent_path]

        sub = Et.SubElement(parent, "Object")
        sub.set("type", attributes["type"])
        sub.set("category", attributes["category"])
        sub.set("name", attributes["name"])
        sub.set("alias", attributes["alias"])
        sub.set("id", attributes["id"])
        sub.set("remark", attributes["remark"])
        sub.set("model", attributes["model"])
        sub.set("time", attributes["time"])
        sub.set("noted", attributes["noted"])
        this, this_path = self.get_elements_with_paths(self.root)[-1]
        self.elements[this_path] = this
        content["this_path"] = this_path
        print(f"[add_element] this_path: {this_path}")
        print(f"[add_element] attributes: {attributes}")
        print(f"[add_element] transform: {transform}")

        tr = Et.SubElement(sub, "Transform")
        pos = Et.SubElement(tr, "position")
        pos.set("x", transform["position"][0])
        pos.set("y", transform["position"][1])
        pos.set("z", transform["position"][2])
        rot = Et.SubElement(tr, "rotation")
        rot.set("x", transform["rotation"][0])
        rot.set("y", transform["rotation"][1])
        rot.set("z", transform["rotation"][2])
        scl = Et.SubElement(tr, "scale")
        scl.set("x", transform["scale"][0])
        scl.set("y", transform["scale"][1])
        scl.set("z", transform["scale"][2])

        return content

    @staticmethod
    def add_properties(content):
        bl_object = bpy.data.collections.get(content["bl_object"])
        attributes = content["attributes"]
        bl_object["ifc_info"] = content['ifc_info'].__str__()
        print(f"[add_properties] bl_props_ifc_info: {bl_object['ifc_info']}")
        bl_object["parent_path"] = content["parent_path"].__str__()
        print(f"[add_properties] bl_props_parent_path: {bl_object['parent_path']}")
        bl_object["this_path"] = content["this_path"].__str__()
        print(f"[add_properties] bl_props_this_path: {bl_object['this_path']}")
        bl_object["type"] = attributes["type"].__str__()
        print(f"[add_properties] bl_props_type: {bl_object['type']}")
        bl_object["category"] = attributes["category"].__str__()
        print(f"[add_properties] bl_props_category: {bl_object['category']}")
        bl_object["name"] = attributes["name"].__str__()
        print(f"[add_properties] bl_props_name: {bl_object['name']}")
        bl_object["alias"] = attributes["alias"].__str__()
        print(f"[add_properties] bl_props_alias: {bl_object['alias']}")
        bl_object["id"] = attributes["id"].__str__()
        print(f"[add_properties] bl_props_id: {bl_object['id']}")
        bl_object["remark"] = attributes["remark"].__str__()
        print(f"[add_properties] bl_props_remark: {bl_object['remark']}")
        bl_object["model"] = attributes["model"].__str__()
        print(f"[add_properties] bl_props_model: {bl_object['model']}")
        bl_object["time"] = attributes["time"].__str__()
        print(f"[add_properties] bl_props_time: {bl_object['time']}")
        bl_object["noted"] = attributes["noted"].__str__()
        print(f"[add_properties] bl_props_noted: {bl_object['noted']}")
        print(f"[add_properties] bl_object: {bl_object.name}")
        return bl_object

    def find_bl_object_by_ifc_info(self, key: str, value: str):
        for obj in self.bl_objects:
            print(f"[find_bl_object_by_ifc_info] obj: {obj}")
            ifc_info = eval(obj["ifc_info"])
            print(f"[find_bl_object_by_ifc_info] ifc_info: {ifc_info}")
            if ifc_info[key] == value:
                print(f"[find_bl_object_by_ifc_info] found: ifc_info[{key}] = {value}")
                return obj
        print(f"[find_bl_object_by_ifc_info] not found: ifc_info[{key}] = {value}")


class BlenderElementTree:
    def __init__(self, element=None):
        self._root = element  # first node


class BlenderOperator:
    @staticmethod
    def get_object_by_name(name) -> bpy.types.Object:
        if name in bpy.data.objects:
            return bpy.data.objects[name]
        return None

    @staticmethod
    def get_collection_by_name(name) -> bpy.types.Collection:
        for col in bpy.data.collections:
            if col.name == name:
                return col
        return None

    @staticmethod
    def get_collection_by_object(obj) -> bpy.types.Collection:
        for col in bpy.data.collections:
            if obj.name in col.objects:
                return col
        return None

    @staticmethod
    def remove_object_from_collection(obj, col) -> None:
        if obj.name in col.objects:
            col.objects.unlink(obj)

    @staticmethod
    def add_object_to_collection(obj, col) -> None:
        col.objects.link(obj)

    def get_children_recursive(self, obj) -> list:
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(self.get_children_recursive(child))
        return children

    def get_hierarchy(self, obj) -> list:
        hierarchy = [obj]
        hierarchy.extend(self.get_children_recursive(obj))
        return hierarchy

    def move_to_collection(self, obj, parent_col) -> None:
        hierarchy = self.get_hierarchy(obj)
        for obj in hierarchy:
            for col in bpy.data.collections:
                if obj.name in col.objects:
                    self.remove_object_from_collection(obj, col)
            self.add_object_to_collection(obj, parent_col)

    def set_parent(self, parent, child) -> bpy.types.Object:
        parent_obj = self.get_object_by_name(parent)
        child_obj = self.get_object_by_name(child)
        if not parent_obj or not child_obj:
            return
        parent_col = self.get_collection_by_object(parent_obj)
        if not parent_col:
            return
        hierarchy = self.get_hierarchy(child_obj)
        for obj in hierarchy:
            self.move_to_collection(obj, parent_col)
            print(f"[command] \"{obj.name}\" has been moved to collection \"{parent_col.name}\"")
        child_obj.parent = parent_obj
        return parent_obj

    def set_parent_by_select(self) -> bpy.types.Object:
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) < 2:
            print("[command] Please select at least 2 objects.")
            return
        parent_obj = bpy.context.active_object
        if parent_obj not in selected_objects:
            print("[command] Please select the parent object.")
            return
        for obj in selected_objects:
            if obj != parent_obj:
                self.set_parent(parent_obj.name, obj.name)
                print(f"[command] \"{obj.name}\" has been set parent to \"{parent_obj.name}\"")
        return parent_obj

    def add_object(self, name, type="EMPTY", parent=None) -> bpy.types.Object:
        bpy.ops.object.add(type=type)
        new_object = bpy.context.active_object
        new_object.name = name
        if parent:
            self.set_parent(parent, new_object.name)
        return new_object


def main():
    # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    # Pre-Settings
    xml_create_settings = XMLCreateSettings.factory("OCMS2_0", "2023.02.16", "Unity")
    # Create
    xml_create = XMLCreate(xml_create_settings)
    xml_create.execute()
    # print(f"collections: {xml_create.collections}")
    # Analysis collection
    # col_building = select_collection("IfcBuilding/")
    # print(f"col_building: {col_building}")


main()
