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

register, unregister = bpy.utils.register_classes_factory(classes)

