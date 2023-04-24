import bpy


class View3dPtMyCustomPanel(bpy.types.Panel):
    # Add panel to View3D UI
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    # Add labels
    bl_category = "My Addon"
    bl_label = "My Panel"

    def draw(self, context):
        row = self.layout.row()
        row.operator("mesh.primitive_cube_add", text="Add Cube")
        # layout = self.layout
        # layout.operator("object.simple_operator")


def register():
    bpy.utils.register_class(View3dPtMyCustomPanel)


def unregister():
    bpy.utils.unregister_class(View3dPtMyCustomPanel)


if __name__ == "__main__":
    register()
