import bpy
import os
from math import radians
from mathutils import Euler

os.system('cls')


class BlenderOperator:
    @staticmethod
    def get_object_collection(ob: bpy.types.Object) -> bpy.types.Collection:
        return next((coll for coll in bpy.data.collections if ob.name in coll.objects), None)

    def get_object_children_recursive(self, ob: bpy.types.Object) -> list:
        return [child for cur_ob in ob.children for child in [cur_ob] + self.get_object_children_recursive(cur_ob)]

    def get_object_hierarchy(self, ob: bpy.types.Object) -> list:
        return [ob] + self.get_object_children_recursive(ob)

    def move_object(self, obj: bpy.types.Object, coll: bpy.types.Collection):
        hierarchy = self.get_object_hierarchy(obj)
        for obj in hierarchy:
            for cur_coll in bpy.data.collections:
                if obj.name in cur_coll.objects:
                    cur_coll.objects.unlink(obj)
            coll.objects.link(obj)

    def set_parent(self, child: bpy.types.Object, parent: bpy.types.Object, move: bool) -> bpy.types.Object:
        if not parent or not child:
            return
        if move:
            # print(f"[set_object_parent] Move \"{child}\" to \"{parent}\"")
            coll = self.get_object_collection(parent)
            hierarchy = self.get_object_hierarchy(child)
            for ob in hierarchy:
                # print(f"[set_object_parent] Move \"{ob}\" to \"{coll}\"")
                if not coll:
                    continue
                self.move_object(ob, coll)
        child.parent = parent

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
                self.set_parent(parent_obj, obj, True)
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

    def add_object(self, name: str, type: str = 'EMPTY', parent: bpy.types.Object = None) -> bpy.types.Object:
        bpy.ops.object.add(type=type)
        new_object = bpy.context.object
        if name:
            new_object.name = name
        if parent:
            self.set_parent(parent, new_object, True)
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
        self.root = bpy.data.collections.get(root)
        self.ifc_objects = {**self.root.all_objects}
        self.ifc_collections = {self.root.name: self.root} | {coll.name: coll for coll in
                                                              self.root.children_recursive}
        self.ifc_info = {}
        self.ifc_extra_list = ["Views", "Types", "StructuralItems", "Members", "Connections"]
        self.ifc_extra_collections = {}
        self.ifc_extra_objects = {}
        self.ifc_extra = {}

        self.is_executed = False

    @staticmethod
    def get_names(source):
        return [ob.name for ob in source]

    def sorting(self):
        for extra in self.ifc_extra_list:
            if extra in self.ifc_collections.keys():
                pop_coll = self.ifc_collections.pop(extra)
                self.ifc_extra_collections[extra] = {pop_coll.name: pop_coll}

                ob_dict = {}
                for ob in pop_coll.all_objects:
                    pop_ob = self.ifc_objects.pop(ob.name)
                    ob_dict[ob.name] = {pop_ob.name: pop_ob}
                self.ifc_extra_objects[extra] = ob_dict

    def read_ifc(self):
        self.ifc_info[self.root.name] = None
        for ob in self.ifc_objects.keys():
            self.ifc_info[ob] = {
                "bl_type": self.define_bl_type(ob),
                "ifc_parent": self.define_ifc_parent(ob),
                "ifc_type": self.define_ifc_type(ob),
                "ifc_project": self.define_ifc_project(ob),
                "ifc_site": self.define_ifc_site(ob),
                "ifc_building": self.define_ifc_building(ob),
                "ifc_storey": self.define_ifc_storey(ob),
                "transform": self.define_transform(ob),
            }

    def define_bl_type(self, ob: str):
        if ob in self.ifc_collections.keys():
            return type(bpy.data.collections.get(ob)).__name__
        return type(bpy.data.objects.get(ob)).__name__

    def define_ifc_parent(self, ob: str):
        for coll in self.ifc_collections.keys():
            if ob in bpy.data.collections[coll].children.keys():
                return coll
            if ob in bpy.data.collections[coll].objects.keys():
                if ob == coll:
                    return None
                return coll

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

    def execute(self):
        self.is_executed = True

        self.sorting()
        print("IFC extra elements has been picked up.")
        self.read_ifc()
        print("IFC elements has been parsed.")


class IFCBuilder:
    def __init__(self, parser: IFCParser):
        self.parser = parser
        self.ifc_info = parser.ifc_info

        self.is_executed = False

    def build(self):
        # Select the root collection.
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection
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
                continue
            parent = self.ifc_info[ifc_parent]["ifc_inst"]
            inst = bpy.data.objects.get(inst)
            parent = bpy.data.objects.get(parent)
            BlenderOperator().set_parent(inst, parent, True)

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

        print("Building new IFC objects...")
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

    def establish(self):
        for ifc_info in self.ifc_info.values():
            obj = ifc_info["ifc_inst"]
            self.elements[obj] = self.Element(bpy.data.objects.get(obj))

    def execute(self):
        if not self.builder.is_executed:
            return print("IFC builder has not been executed, would not build ETree.")

        self.establish()
        for obj, ifc_elem in self.elements.items():
            ifc_elem.set_attr("id", "my_custom_id")
            # print(f"Element {obj} has been added to ETree, with element {ifc_elem}.")

        print("IFC ETree elements has been set attributes.")
        #
        # for obj, ifc_elem in self.elements.items():
        #     ifc_elem.remove_attr("id")
        #
        # print("IFC ETree elements has been removed attributes.")


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
    # ifc_parser = IFCParser("IfcBuilding/高雄港埠旅運中心")
    ifc_parser = IFCParser("IfcProject/")
    ifc_parser.execute()
    ifc_builder = IFCBuilder(ifc_parser)
    ifc_builder.execute()
    blender_etree = IFCETree(ifc_builder)
    blender_etree.execute()
