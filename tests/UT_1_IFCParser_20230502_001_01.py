import bpy
import os

os.system('cls')


class IFCParser:
    def __init__(self, ifc_root="IfcBuilding/"):
        self.root = bpy.data.collections.get(ifc_root)
        self.bl_collections = [self.root.name] + self.convert_to_names(self.root.children_recursive)
        self.bl_objects = self.root.all_objects.keys()
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
        self.ifc_elements[self.root.name] = None
        for obj in self.bl_objects:
            print(f"\nobj: {obj}")
            content["bl_type"] = self.define_bl_type(obj)
            print(f"bl_type: {content['bl_type']}")
            content["ifc_parent"] = self.define_ifc_parent(obj)
            print(f"ifc_parent: {content['ifc_parent']}")
            content["ifc_type"] = self.define_ifc_type(obj)
            print(f"ifc_type: {content['ifc_type']}")
            content["ifc_project"] = self.define_ifc_project(obj)
            print(f"ifc_project: {content['ifc_project']}")
            content["ifc_site"] = self.define_ifc_site(obj)
            print(f"ifc_site: {content['ifc_site']}")
            content["ifc_building"] = self.define_ifc_building(obj)
            print(f"ifc_building: {content['ifc_building']}")
            content["ifc_storey"] = self.define_ifc_storey(obj)
            print(f"ifc_storey: {content['ifc_storey']}")
            content["ifc_transform"] = self.define_ifc_transform(obj)
            print(f"ifc_transform: {content['ifc_transform']}")
            # TODO: et_path: root/高雄港埠旅運中心/15FL
            self.ifc_elements[obj] = dict(content)

    def define_bl_type(self, obj):
        if obj in self.bl_collections:
            return type(bpy.data.collections.get(obj)).__name__
        return type(bpy.data.objects.get(obj)).__name__

    def define_ifc_parent(self, obj):
        for col in self.bl_collections:
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
        print("IFC Elements has been parsed.")


if __name__ == "__main__":
    op = IFCParser("IfcBuilding/高雄港埠旅運中心")
    op.execute()
