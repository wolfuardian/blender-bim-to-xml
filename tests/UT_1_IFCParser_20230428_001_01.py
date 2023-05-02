import bpy
import os

os.system('cls')


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

    def define_parent(self):
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
            print("ifc_tree is empty")
            return
        for child in self.ifc_tree.keys():
            if child in self.bl_collections:
                self.ifc_type[child] = "collection"
            else:
                self.ifc_type[child] = "object"

    def execute(self):
        self.define_parent()
        self.define_type()


if __name__ == "__main__":
    op = IFCParser("IfcBuilding/高雄港埠旅運中心")
    op.execute()
