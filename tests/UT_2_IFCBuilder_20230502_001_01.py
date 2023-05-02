import bpy
import os
from math import radians
from mathutils import Euler

os.system('cls')


class BlenderOperator:
    @staticmethod
    def get_object_by_name(name) -> bpy.types.Object:
        if name in bpy.data.objects:
            return bpy.data.objects[name]
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
        if parent_col:
            hierarchy = self.get_hierarchy(child_obj)
            for obj in hierarchy:
                self.move_to_collection(obj, parent_col)
                # print(f"\"{obj.name}\" has been moved to collection \"{parent_col.name}\"")
        child_obj.parent = parent_obj
        # print(f"\"{child_obj.name}\" has been set parent to \"{parent_obj.name}\"")
        return parent_obj

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
        self.ifc_collections = [self.bl_root.name] + self.convert_to_names(self.bl_root.children_recursive)
        self.ifc_objects = self.bl_root.all_objects.keys()
        self.ifc_elements = {}

        self.is_executed = False

    @staticmethod
    def convert_to_names(objects_or_collections):
        names = []
        for obj in objects_or_collections:
            names.append(obj.name)
        return names

    def read_ifc(self):
        content = {}
        self.ifc_elements[self.bl_root.name] = None
        for obj in self.ifc_objects:
            content["bl_type"] = self.define_bl_type(obj)
            content["ifc_parent"] = self.define_ifc_parent(obj)
            content["ifc_type"] = self.define_ifc_type(obj)
            content["ifc_project"] = self.define_ifc_project(obj)
            content["ifc_site"] = self.define_ifc_site(obj)
            content["ifc_building"] = self.define_ifc_building(obj)
            content["ifc_storey"] = self.define_ifc_storey(obj)
            content["ifc_transform"] = self.define_ifc_transform(obj)
            self.ifc_elements[obj] = dict(content)

    def define_bl_type(self, obj):
        if obj in self.ifc_collections:
            return type(bpy.data.collections.get(obj)).__name__
        return type(bpy.data.objects.get(obj)).__name__

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
    def define_ifc_transform(obj):
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

    def execute(self):
        self.is_executed = True

        self.read_ifc()
        print("IFC elements has been parsed.")


class IFCBuilder:
    def __init__(self, parser: IFCParser):
        self.parser = parser
        self.ifc_elements = parser.ifc_elements
        self.ifc_instances = {}

        self.is_executed = False

    def build(self):
        if not self.ifc_elements:
            print("IFC elements has not been parsed, would not build IFC objects.")
            return
        for obj, elem in self.ifc_elements.items():
            self.ifc_instances[obj] = BlenderOperator().add_object(obj).name

    def assemble(self):
        for obj, inst in self.ifc_instances.items():
            ifc_parent = self.ifc_elements[obj]["ifc_parent"]
            if not ifc_parent:
                continue
            parent = self.ifc_instances[ifc_parent]
            BlenderOperator().set_parent(parent, inst)

    def set_transform(self):
        for obj, inst in self.ifc_instances.items():
            transform = self.ifc_elements[obj]["ifc_transform"]
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


if __name__ == "__main__":
    ifc_parser = IFCParser("IfcBuilding/高雄港埠旅運中心")
    ifc_parser.execute()
    ifc_builder = IFCBuilder(ifc_parser)
    ifc_builder.execute()
