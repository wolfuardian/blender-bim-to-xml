import bpy
import os

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
            print("Please select at least 2 objects.")
            return
        parent_obj = bpy.context.active_object
        if parent_obj not in selected_objects:
            print("Please select the parent object.")
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
            print(f"Collection \"{root_col}\" not found.")
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
            # TODO: et_path: root/高雄港埠旅運中心/15FL
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
            "position": [
                obj.matrix_world.to_translation().x.__str__(),
                obj.matrix_world.to_translation().y.__str__(),
                obj.matrix_world.to_translation().z.__str__()
            ],
            "rotation": [
                obj.matrix_world.to_euler().x.__str__(),
                obj.matrix_world.to_euler().y.__str__(),
                obj.matrix_world.to_euler().z.__str__()
            ],
            "scale": [
                obj.matrix_world.to_scale().x.__str__(),
                obj.matrix_world.to_scale().y.__str__(),
                obj.matrix_world.to_scale().z.__str__()
            ]
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
        self.instances = {}

        self.is_executed = False

    def build(self):
        if not self.ifc_elements:
            print("IFC elements has not been parsed, would not build IFC objects.")
            return
        for obj, elem in self.ifc_elements.items():
            self.instances[obj] = BlenderOperator().add_object(obj).name

    def assemble(self):
        for obj, inst in self.instances.items():
            ifc_parent = self.ifc_elements[obj]["ifc_parent"]
            if not ifc_parent:
                continue
            parent = self.instances[ifc_parent]
            BlenderOperator().set_parent(parent, inst)

    def execute(self):
        self.is_executed = True
        if not self.parser.is_executed:
            return print("IFC Parser has not been executed, would not build IFC objects.")

        self.build()
        self.assemble()
        print("New IFC objects has been built.")


if __name__ == "__main__":
    ifc_parser = IFCParser("IfcBuilding/高雄港埠旅運中心")
    ifc_parser.execute()
    ifc_builder = IFCBuilder(ifc_parser)
    ifc_builder.execute()


class BlenderETree:
    def __init__(self, builder: IFCBuilder):
        self.builder = builder
        self.ifc_root = builder.ifc_root
        self.ifc_type = builder.ifc_type
        self.ifc_inherit = builder.ifc_inherit
        self.ifc_objects = builder.ifc_objects
        self.ifc_objects_partners = builder.ifc_objects_partners

    def establish(self):
        pass

    def execute(self):
        if not self.builder.is_executed:
            return print("IFC builder has not been executed, would not build ETree.")

        self.establish()


if __name__ == "__main__":
    ifc_parser = IFCParser("IfcBuilding/高雄港埠旅運中心")
    ifc_parser.execute()
    ifc_builder = IFCBuilder(ifc_parser)
    ifc_builder.execute()
    blender_etree = BlenderETree(ifc_builder)
    blender_etree.execute()
