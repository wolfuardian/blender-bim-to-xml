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
    def __init__(self, ifc_root="IfcBuilding/"):
        self.root = bpy.data.collections.get(ifc_root)
        self.ifc_collections = [self.root.name] + self.convert_to_names(self.root.children_recursive)
        self.ifc_objects = self.root.all_objects.keys()
        self.ifc_types = {}
        self.ifc_inherit = {}

        self.is_executed = False

    @staticmethod
    def convert_to_names(objects_or_collections):
        names = []
        for obj in objects_or_collections:
            names.append(obj.name)
        return names

    def define_inherit(self):
        self.ifc_inherit[self.root.name] = None
        for parent in self.ifc_objects:
            # Only if the object is a transform (parent) object
            if parent not in self.ifc_collections:
                continue
            for child in bpy.data.collections[parent].objects.keys():
                # If the child is the same as the parent, then it is the root object
                if child == parent:
                    for collection in self.ifc_collections:
                        if bpy.data.collections[parent].name not in bpy.data.collections[collection].children.keys():
                            continue
                        self.ifc_inherit[child] = collection
                        break
                    continue
                self.ifc_inherit[child] = parent

    def define_types(self):
        if not self.ifc_inherit:
            return
        for child in self.ifc_inherit.keys():
            if child in self.ifc_collections:
                self.ifc_types[child] = "collection"
            else:
                self.ifc_types[child] = "object"

    def execute(self):
        self.is_executed = True

        self.define_inherit()
        print("IFC tree has been defined.")


class IFCBuilder:
    def __init__(self, parser: IFCParser):
        self.ifc_parser = parser
        self.ifc_root = parser.root.name
        self.ifc_type = parser.ifc_types
        self.ifc_inherit = parser.ifc_inherit
        self.ifc_objects = parser.ifc_objects
        self.ifc_objects_partners = {}

        self.is_executed = False

    def build(self):
        if not self.ifc_inherit:
            print("IFC objects inherit is empty")
            return
        for child, parent in self.ifc_inherit.items():
            if child in self.ifc_objects:
                self.ifc_objects_partners[child] = BlenderOperator().add_object(child).name

    def assemble(self):
        for ifc, obj in self.ifc_objects_partners.items():
            ifc_parent = self.ifc_inherit.get(ifc)
            if not ifc_parent:
                continue
            parent = self.ifc_objects_partners[ifc_parent]
            BlenderOperator().set_parent(parent, obj)

    def execute(self):
        self.is_executed = True
        if not self.ifc_parser.is_executed:
            return print("IFC parser has not been executed, would not build IFC objects.")

        self.build()
        self.assemble()
        print("New IFC building has been built.")


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
