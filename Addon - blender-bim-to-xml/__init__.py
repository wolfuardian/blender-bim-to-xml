import bpy

bl_info = {
    "name": "blender-bim-to-xml",
    "author": "Wolfuardian",
    "description": "",
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}

classes = (
)


# class SimpleOperator(bpy.types.Operator):
#     bl_idname = "object.simple_operator"
#     bl_label = "Create Cube"
#     bl_options = {'REGISTER', 'UNDO'}
#
#     def exec(self, context):
#         bpy.ops.mesh.primitive_cube_add()
#         return {'FINISHED'}
#
#
# class SimplePanel(bpy.types.Panel):
#     bl_label = "My Addon"
#     bl_idname = "OBJECT_PT_simple_panel"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = "My Addon"
#
#     def draw(self, context):
#         layout = self.layout
#         layout.operator("object.simple_operator")


# 
# def register():
#     bpy.utils.register_class(SimpleOperator)
#     bpy.utils.register_class(SimplePanel)
# 
# 
# def unregister():
#     bpy.utils.unregister_class(SimpleOperator)
#     bpy.utils.unregister_class(SimplePanel)


register, unregister = bpy.utils.register_classes_factory(classes)
