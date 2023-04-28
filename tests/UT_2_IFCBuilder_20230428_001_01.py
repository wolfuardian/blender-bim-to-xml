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
        if not parent_col:
            return
        hierarchy = self.get_hierarchy(child_obj)
        for obj in hierarchy:
            self.move_to_collection(obj, parent_col)
            print(f"\"{obj.name}\" has been moved to collection \"{parent_col.name}\"")
        child_obj.parent = parent_obj
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
                print(f"\"{obj.name}\" has been set parent to \"{parent_obj.name}\"")
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

    def add_object(self, name, type="EMPTY", parent=None) -> bpy.types.Object:
        bpy.ops.object.add(type=type)
        new_object = bpy.context.active_object
        new_object.name = name
        if parent:
            self.set_parent(parent, new_object.name)
        return new_object


class IFCParser:
    def __init__(self, ifc_root="IfcBuilding/"):
        self.root = bpy.data.collections.get(ifc_root)
        self.bl_collections = [self.root.name] + self.convert_to_names(self.root.children_recursive)
        self.bl_objects = self.root.all_objects.keys()
        self.ifc_tree = {}
        self.ifc_type = {}

    @staticmethod
    def convert_to_names(objects_or_collections):
        names = []
        for obj in objects_or_collections:
            names.append(obj.name)
        return names

    def define_ifc_tree(self):
        self.ifc_tree[self.root.name] = None
        for parent in self.bl_objects:
            # Only if the object is a transform (parent) object
            if parent not in self.bl_collections:
                continue
            for child in bpy.data.collections[parent].objects.keys():
                # If the child is the same as the parent, then it is the root object
                if child == parent:
                    for collection in self.bl_collections:
                        if bpy.data.collections[parent].name not in bpy.data.collections[collection].children.keys():
                            continue
                        self.ifc_tree[child] = collection
                        break
                    continue
                self.ifc_tree[child] = parent

    def define_type(self):
        if not self.ifc_tree:
            return
        for child in self.ifc_tree.keys():
            if child in self.bl_collections:
                self.ifc_type[child] = "collection"
            else:
                self.ifc_type[child] = "object"

    def execute(self):
        print(f"start defining ifc_tree")
        self.define_ifc_tree()
        for child, parent in self.ifc_tree.items():
            print(f"parent: {parent}, child: {child}")
        print(f"total ifc_tree: {len(self.ifc_tree.items())}")
        print(f"\nstart defining type")
        self.define_type()
        for child, type in self.ifc_type.items():
            print(f"type: {type}, child: {child}")
        print(f"total ifc_type: {len(self.ifc_type.items())}")


class IFCBuilder:
    def __init__(self, parser: IFCParser):
        self.ifc_parser = parser
        self.ifc_tree = parser.ifc_tree
        self.ifc_type = parser.ifc_type
        self.bl_collections = parser.bl_collections
        self.bl_objects = parser.bl_objects
        self.ifc_root = parser.root.name
        self.ifc_objects = {}

    def build_tree_objects(self):

        if not self.ifc_tree:
            print("IFC tree is empty")
            return
        print(f"\nstart building objects")
        for child, parent in self.ifc_tree.items():
            if child in self.bl_objects:
                self.ifc_objects[child] = BlenderOperator().add_object(child)
                print(f"\"{self.ifc_objects[child].name}\" has been added")

        print(f"\nstart checking objects")
        for obj_name, obj in self.ifc_objects.items():
            print(f"\"{obj_name}\" -> {obj.name}")

        print(f"total {len(self.ifc_objects)} objects have been added")

    def execute(self):
        self.ifc_parser.execute()
        self.build_tree_objects()


if __name__ == "__main__":
    ifc_parser = IFCParser("IfcBuilding/高雄港埠旅運中心")
    ifc_builder = IFCBuilder(ifc_parser)
    ifc_builder.execute()
