import bpy
import os
from math import radians
from mathutils import Euler
from datetime import datetime

os.system('cls')


class BlenderOperator:
    @staticmethod
    def get_object_by_name(name) -> bpy.types.Object:
        if not name:
            return None
        if name in bpy.data.objects:
            return bpy.data.objects[name]
        return None

    @staticmethod
    def get_inherit_coll(obj: str) -> str:
        for col in bpy.data.collections:
            if not obj:
                continue
            if obj in col.objects:
                return col.name
        return ''

    @staticmethod
    def unlink_ob(ob: str, coll: str):
        print(f"[unlink_ob] \"{ob}\" has been unlinked from \"{coll}\".")
        if ob in bpy.data.collections.get(coll).objects:
            bpy.data.collections.get(coll).objects.unlink(bpy.data.objects.get(ob))

    @staticmethod
    def link_ob(ob: str, coll: str):
        print(f"[link_ob] \"{ob}\" has been linked to \"{coll}\".")
        if coll:
            bpy.data.collections.get(coll).objects.link(bpy.data.objects.get(ob))
        else:
            bpy.context.scene.collection.objects.link(bpy.data.objects.get(ob))

    def get_ob_children_recurse(self, ob: str) -> list[str]:
        children = []
        for child in bpy.data.objects.get(ob).children:
            children.append(child.name)
            children.extend(self.get_ob_children_recurse(child.name))
        return children

    def get_hierarchy(self, ob: str) -> list[str]:
        hierarchy = [ob]
        hierarchy.extend(self.get_ob_children_recurse(ob))
        return hierarchy

    def move_ob_to_coll(self, source: str, target: str) -> None:
        hierarchy = self.get_hierarchy(source)
        print(f"[move_ob_to_coll] hierarchy: {hierarchy}")
        for ob in hierarchy:
            for coll in bpy.data.collections:
                # print(f"[move_ob_to_coll] \"{ob}\" in \"{coll}\"")
                if ob in coll.objects:
                    self.unlink_ob(ob, coll.name)
            # print(f"[move_ob_to_coll] \"{ob}\" has been moved to \"{target}\".")
            self.link_ob(ob, target)

    def set_parent(self, child: str, parent: str) -> str:
        print(f"[set_parent] child: {child}, parent: {parent}")
        coll = self.get_inherit_coll(parent)
        print(f"[set_parent] coll: {coll}")
        hierarchy = self.get_hierarchy(child)
        for ob in hierarchy:
            self.move_ob_to_coll(ob, coll)
        if parent:
            bpy.data.objects.get(child).parent = bpy.data.objects.get(parent)
        return parent

    def set_parent_by_select(self) -> bpy.types.Object:
        selected_objects = bpy.context.selected_objects
        if len(selected_objects) < 2:
            print("[set_parent_by_select] Please select at least 2 objects.")
            return
        parent_obj = bpy.context.active_object
        if parent_obj not in selected_objects:
            print("[set_parent_by_select] Please select the parent object.")
            return
        for obj in selected_objects:
            if obj != parent_obj:
                self.set_parent(parent_obj.name, obj.name)
                # print(f"\"{obj.name}\" has been set parent to \"{parent_obj.name}\"")
        return parent_obj

    @staticmethod
    def reduce_ifc_objects(root_col, keep=None):
        def reduce(col):
            to_remove = [obj for obj in col.objects if obj.name != col.name]
            if keep:
                to_remove = to_remove[:-keep]
            for obj in to_remove:
                print(f"Remove \"{obj.name}\" from \"{col.name}\"")
                col.objects.unlink(obj)

        def traverse(col):
            reduce(col)
            for child in col.children:
                traverse(child)

        if root_col not in bpy.data.collections:
            print(f"[reduce_ifc_objects] Collection \"{root_col}\" not found.")
            return
        traverse(bpy.data.collections.get(root_col))

    def add_object(self, name=None, type="EMPTY", parent=None) -> bpy.types.Object:
        bpy.ops.object.add(type=type)
        new_object = bpy.context.object
        if name:
            new_object.name = name
        if parent:
            self.set_parent(parent, new_object.name)
        # print(f"\"{new_object.name}\" has been added.")
        return new_object

    @staticmethod
    def set_location(obj: str, location: tuple) -> None:
        obj = bpy.data.objects.get(obj)
        if not obj:
            print(f"[set_location] Object {obj} not found")
            return
        obj.location = location

    @staticmethod
    def set_rotation(obj, rotation, use_degree=False):
        obj = bpy.data.objects.get(obj)
        if not obj:
            print(f"[set_location] Object {obj} not found")
            return
        if use_degree:
            rotation = tuple(radians(angle) for angle in rotation)
        obj.rotation_euler = Euler(rotation)

    @staticmethod
    def set_scale(obj, scale):
        obj = bpy.data.objects.get(obj)
        if not obj:
            print(f"[set_location] Object {obj} not found")
            return
        obj.scale = scale


class IFCParser:
    def __init__(self, root="IfcBuilding/"):
        self.bl_root = bpy.data.collections.get(root)
        self.ifc_ignore = ["Views", "Types", "StructuralItems", "Members", "Connections"]
        self.ifc_collections = []
        self.ifc_objects = []
        self.ifc_info = {}
        self.ifc_types = {}  # The type of the object, e.g. IfcWall, IfcWindow, IfcDoor, etc.
        self.init_ifc_collections()
        self.init_ifc_objects()

        self.scene_collection = bpy.context.scene.collection

        self.is_executed = False

    def init_ifc_collections(self):
        self.ifc_collections = [self.bl_root.name] + self.convert_to_names(self.bl_root.children_recursive)
        for col in self.ifc_collections:
            if col in self.ifc_ignore:
                self.ifc_collections.remove(col)

    def init_ifc_objects(self):
        self.ifc_objects = self.bl_root.all_objects.keys()

    @staticmethod
    def convert_to_names(objects_or_collections):
        names = []
        for obj in objects_or_collections:
            names.append(obj.name)
        return names

    def read_ifc(self):
        content = {}
        self.ifc_info[self.bl_root.name] = None
        for obj in self.ifc_objects:
            content["ifc_parent"] = self.define_ifc_parent(obj)
            if content["ifc_parent"] in self.ifc_ignore:
                self.ifc_types[obj] = bpy.data.objects.get(obj)
                continue
            content["ifc_type"] = self.define_ifc_type(obj)
            content["ifc_project"] = self.define_ifc_project(obj)
            content["ifc_site"] = self.define_ifc_site(obj)
            content["ifc_building"] = self.define_ifc_building(obj)
            content["ifc_storey"] = self.define_ifc_storey(obj)
            # content["bl_type"] = self.define_bl_type(obj)
            content["transform"] = self.define_transform(obj)
            content["attributes"] = self.define_attributes(obj)
            self.ifc_info[obj] = dict(content)

    # def define_bl_type(self, obj):
    #     if obj in self.ifc_collections:
    #         return type(bpy.data.collections.get(obj)).__name__
    #     return type(bpy.data.objects.get(obj)).__name__

    def define_ifc_parent(self, obj):
        for col in self.ifc_collections:
            if obj in bpy.data.collections[col].children.keys():
                return col
            if obj in bpy.data.collections[col].objects.keys():
                if obj == col:
                    return None
                return col

    @staticmethod
    def define_ifc_type(obj):
        if obj.startswith("Ifc"):
            return obj.split("/")[0]

    @staticmethod
    def define_ifc_project(obj):
        if obj.startswith("IfcProject/"):
            return obj.split("/")[1]

    @staticmethod
    def define_ifc_site(obj):
        if obj.startswith("IfcSite/"):
            return obj.split("/")[1]

    @staticmethod
    def define_ifc_building(obj):
        if obj.startswith("IfcBuilding/"):
            return obj.split("/")[1]

    @staticmethod
    def define_ifc_storey(obj):
        if obj.startswith("IfcBuildingStorey/"):
            return obj.split("/")[1]

    @staticmethod
    def define_transform(obj):
        obj = bpy.data.objects[obj]
        transform = {
            "position": (
                obj.matrix_world.to_translation().x,
                obj.matrix_world.to_translation().y,
                obj.matrix_world.to_translation().z
            ),
            "rotation": (
                obj.matrix_world.to_euler().x,
                obj.matrix_world.to_euler().y,
                obj.matrix_world.to_euler().z
            ),
            "scale": (
                obj.matrix_world.to_scale().x,
                obj.matrix_world.to_scale().y,
                obj.matrix_world.to_scale().z
            )
        }
        return transform

    def define_attributes(self, obj):
        attributes = {
            "type": self.define_ifc_type(obj),
            "category": "0",
            "name": obj.split("/")[0],
            "alias": obj,
            "id": "",
            "remark": "",
            "model": obj.split("/")[0],
            "time": self.get_date_time(),
            "noted": "created"
        }
        return attributes

    @staticmethod
    def get_date_time():
        dt = datetime.now()
        return dt.strftime("%Y/%m/%d %H:%M")

    def execute(self):
        self.is_executed = True

        self.read_ifc()
        print("IFC elements has been parsed.")


class IFCBuilder:
    def __init__(self, parser: IFCParser):
        self.parser = parser
        self.ifc_info = parser.ifc_info

        self.is_executed = False

    def build(self):
        if not self.ifc_info:
            print("IFC elements has not been parsed, would not build IFC objects.")
            return
        for obj, elem in self.ifc_info.items():
            self.ifc_info[obj]["ifc_inst"] = BlenderOperator().add_object(obj).name

    def assemble(self):
        for obj, ifc_info in self.ifc_info.items():
            inst = self.ifc_info[obj]["ifc_inst"]
            ifc_parent = self.ifc_info[obj]["ifc_parent"]
            if not ifc_parent:
                print("No parent found for object: {}".format(obj))
                # BlenderOperator().move_to_collection(inst, bpy.context.scene.collection)
                BlenderOperator().set_parent(inst, '')
                continue
            parent = self.ifc_info[ifc_parent]["ifc_inst"]
            BlenderOperator().set_parent(inst, parent)

    def set_transform(self):
        for obj, ifc_info in self.ifc_info.items():
            inst = self.ifc_info[obj]["ifc_inst"]
            transform = self.ifc_info[obj]["transform"]
            position = transform["position"]
            rotation = transform["rotation"]
            scale = transform["scale"]
            BlenderOperator().set_location(inst, position)
            BlenderOperator().set_rotation(inst, rotation)
            BlenderOperator().set_scale(inst, scale)

    def execute(self):
        self.is_executed = True
        if not self.parser.is_executed:
            return print("IFC Parser has not been executed, would not build IFC objects.")

        self.build()
        self.assemble()
        self.set_transform()
        print("New IFC objects has been built.")


class IFCETree:
    def __init__(self, builder: IFCBuilder):
        self.builder = builder
        self.ifc_info = builder.ifc_info
        self.elements = {}
        self.attributes = {}

    class Element:
        def __init__(self, obj=None):
            self.obj = obj
            self.attributes = {}
            self.children = []

        def set_attr(self, key, value):
            self.attributes[key] = value
            self.obj[key] = value

        def remove_attr(self, key):
            if key in self.attributes:
                del self.attributes[key]
                del self.obj[key]

        def update_attr(self, key, new_value):
            if key in self.attributes:
                self.attributes[key] = new_value
                self.obj[key] = new_value

        def __repr__(self):
            return f"<IFCElement '{self.obj.name}'>"

    @staticmethod
    def add_properties(element, content):
        attributes = content["attributes"]
        element.set_attr("type", attributes["type"].__str__())
        element.set_attr("category", attributes["category"].__str__())
        element.set_attr("name", attributes["name"].__str__())
        element.set_attr("alias", attributes["alias"].__str__())
        element.set_attr("remark", attributes["remark"].__str__())
        element.set_attr("model", attributes["model"].__str__())
        element.set_attr("time", attributes["time"].__str__())
        element.set_attr("noted", attributes["noted"].__str__())

        # bl_object["ifc_info"] = content['ifc_info'].__str__()
        # print(f"[add_properties] bl_props_ifc_info: {bl_object['ifc_info']}")
        # bl_object["parent_path"] = content["parent_path"].__str__()
        # print(f"[add_properties] bl_props_parent_path: {bl_object['parent_path']}")
        # bl_object["this_path"] = content["this_path"].__str__()
        # print(f"[add_properties] bl_props_this_path: {bl_object['this_path']}"

    def establish(self):
        for content in self.ifc_info.values():
            inst = content["ifc_inst"]
            self.elements[inst] = self.Element(bpy.data.objects.get(inst))
            self.add_properties(self.elements[inst], content)

    def execute(self):
        if not self.builder.is_executed:
            return print("IFC builder has not been executed, would not build ETree.")

        self.establish()
        for obj, ifc_elem in self.elements.items():
            ifc_elem.set_attr("id", "my_custom_id")
            # print(f"Element {obj} has been added to ETree, with element {ifc_elem}.")

        print("IFC ETree elements has been set attributes.")

        for obj, ifc_elem in self.elements.items():
            ifc_elem.remove_attr("id")

        print("IFC ETree elements has been removed attributes.")


#
#
# class BlenderElement:
#     def __init__(self, obj_name):
#         self.obj = bpy.data.objects.get(obj_name)
#         if self.obj is None:
#             print(f"Object {obj_name} not found")
#             return
#         self.attributes = {}
#
#     def set_attr(self, key, value):
#         self.attributes[key] = value
#         self.obj[key] = value
#
#     def remove_attr(self, key):
#         if key in self.attributes:
#             del self.attributes[key]
#             del self.obj[key]
#
#     def update_attr(self, key, new_value):
#         if key in self.attributes:
#             self.attributes[key] = new_value
#             self.obj[key] = new_value
#
#     def __repr__(self):
#         return f"<BlenderElement '{self.obj.name}'>"
#
#
# # 使用範例
# object_name = "IfcBuildingStorey/B2FL"
# blender_element = BlenderElement(object_name)
# blender_element.set_attr("id", "my_custom_id")
#
# print(blender_element.attributes)  # 輸出：{'id': 'my_custom_id'}
# print(blender_element.obj["id"])  # 輸出：my_custom_id
#
# # 更新 id 屬性
# blender_element.update_attr("id", "updated_id")
#
# # 移除 id 屬性
# blender_element.remove_attr("id")
# print(blender_element.attributes)  # 輸出：{'id': 'my_custom_id'}

if __name__ == "__main__":
    ifc_parser = IFCParser("IfcProject/")
    ifc_parser.execute()
    ifc_builder = IFCBuilder(ifc_parser)
    ifc_builder.execute()
    blender_etree = IFCETree(ifc_builder)
    blender_etree.execute()
