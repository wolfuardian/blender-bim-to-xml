# ------------------------------------------------------------------------------------------
# EoBatchFBXExportor (B3D to Maya) UnitTest
# ------------------------------------------------------------------------------------------

import bpy
import re
import os

os.system('cls')


def create_col(str, parent):
    if not bpy.context.scene.collection.children.get(str):
        exist_col = bpy.data.collections.get(str)
        if exist_col:
            parent.children.link(exist_col)
            #            print(">>> \"{}\" already exists, has moved to this scene.".format(str))
            return exist_col
        else:
            new_col = bpy.data.collections.new(str)
            parent.children.link(new_col)
            #            print(">>> \"{}\" has been created successfully.".format(str))
            return new_col
    else:
        #        print(">>> \"{}\" already exists.".format(str))
        return bpy.context.scene.collection.children.get(str)


# def select_col(str):
#     cols = bpy.context.view_layer.layer_collection.children

#     if(bpy.context.collection.name == str):
#         return bpy.context.collection

#     for col in cols:
#         if col.name == str:
#             bpy.context.view_layer.active_layer_collection = col
#             return bpy.context.collection


def select_col(str):
    cols = bpy.context.view_layer.layer_collection.children

    def search(col):
        for col in col.children:
            if col.name == str:
                bpy.context.view_layer.active_layer_collection = col
            search(col)

    search(bpy.context.view_layer.layer_collection)
    return bpy.context.collection


def export_fbx(target):
    mesh_objects = [o for o in target.objects if o.type == 'MESH']

    if mesh_objects and bpy.context.mode == 'OBJECT':

        bpy.ops.object.select_all(action='DESELECT')

        for o in mesh_objects:
            o.select_set(True)

        # Export the modified objects to FBX

        blend_path = bpy.path.abspath("//")

        folder = re.split('_', target.name, 1)[0]
        dir = "{}/fbx/{}/".format(blend_path, folder)

        if not os.path.exists(dir):
            os.makedirs(dir)

        bpy.ops.export_scene.fbx(
            filepath=bpy.path.abspath("{}{}_GP.fbx".format(dir, target.name)),
            use_selection=True)

        # Delete all duplicates
        bpy.ops.object.select_all(action='DESELECT')


def create_col_recursion(str, parent, limit=3, offset=0):
    pattern = r'[/:-]'
    splits = re.split(pattern, str)
    depth_total = limit + offset if len(splits) > limit else len(splits) + offset

    current = parent.name + '_' + str
    target = bpy.data.collections.get(str)

    objs = [o for o in target.objects] if target else [bpy.data.objects.get(str)]

    def recurse(current, parent, depth):
        re_current = re.split(pattern, current, 1)
        next = re_current[0] + '_' + re_current[1]

        exist_col = bpy.data.collections.get(re_current[0])

        if not exist_col:
            exist_col = create_col(re_current[0], parent)

        # Moves the object to a new collection at the last recursion.
        if depth == 1:
            # print(">>> \"{}\" <<<.".format(exist_col.name))
            for o in objs:

                if not bpy.data.collections.get(re_current[0]):
                    o.name = current
                else:
                    o.name = re_current[0]

                if o.type == 'MESH':
                    print('>>> Decimate modifier added to \"{}\".'.format(o.name))
                    print(o.BIMAttributeProperties.ifc_definition_id)
                    # obj = bpy.data.objects.get('IfcBuildingElementProxy/衛生間隔板-門:衛生間隔板.134')

                    # Modify
                    mod = o.modifiers.get("Decimate")
                    if mod is None:
                        # otherwise add a modifier to selected object
                        mod = o.modifiers.new('Decimate', type='DECIMATE')
                        mod.decimate_type = 'DISSOLVE'

                exist_col.objects.link(o)

        if depth > 1:
            recurse(next, bpy.data.collections.get(re_current[0]), depth - 1)

    recurse(current, parent, depth_total)  # starts the recursion


def rename_recurse(pattern, sub, str):
    target = bpy.data.collections.get(str)
    if not target:
        return

    def recurse(current):
        current.name = re.sub(pattern, sub, current.name)
        for o in [o for o in current.objects]:
            o.name = re.sub(pattern, sub, o.name)

        if not current.children:
            return

        for next in current.children:
            recurse(next)

    recurse(target)  # starts the recursion
    return re.sub(pattern, sub, str)


def export_fbx_recurse(str):
    all_cols_sets = [c for c in bpy.data.collections]
    total = float(len(all_cols_sets))

    target = bpy.data.collections.get(str)
    if not target:
        return

    def recurse(current):
        if current.objects:
            export_fbx(current)
            cur = total - len(all_cols_sets)
            percentage = round((cur / total) * 100, 2)
            p = progress_bar(percentage, '#', 40)
#            print(">>> fbx progress rate: [{}]  {} % ({}/{}) / \"{}\" done.".format(p, percentage, int(cur), int(total),
#                                                                                    current.name))
            cur = cur + 1

        all_cols_sets.remove(current)

        if not current.children:
            return

        for next in current.children:
            recurse(next)

    recurse(target)  # starts the recursion


def remap(value, omin, omax, nmin, nmax):
    return (((value - omin) * (nmax - nmin)) / (omax - omin)) + nmin


def progress_bar(percentage, item, length):  # 0-100
    bar = ''
    for i in range(0, length):
        bar = bar + ' '
    percent_i = round(remap(percentage, 0, 100, 1, length))
    return re.sub(' ', item, bar, int(percent_i))


def run_batch():
    # ------------------------------------
    # User defined
    # ------------------------------------
    prefix_name = '__inst__'
    root_col_name = 'IfcBuilding/'
    # ------------------------------------

    if prefix_name == '':
        prefix_name = '_'

    print("")
    print("------------------------------")
    print("--- STARTING PROGRESS SOON ---")
    print("------------------------------")
    print("")

    # ------------------------------------
    # Step 1
    # ------------------------------------
    if not bpy.data.collections.get(root_col_name):
        # print(">>> \"{}\" not found, will end the script.".format(root_col_name))
        # Exit the script.
        return

    # Fix the ignore string.
    root_col = select_col(root_col_name)
    # rename_recurse('[^A-Za-z0-9/:_]', 'x', root_col.name)
    # print(">>> \"{}\" has found that the script will be executed.".format(root_col.name))
    root_col_new = create_col(prefix_name + root_col_name, bpy.context.scene.collection)

    # ------------------------------------
    # Step 2
    # ------------------------------------
    # Loop each Layer-Col

    layer_col_sets = [c for c in root_col.children]
    for layer_col in layer_col_sets:
        layer_col_name = prefix_name + 'Ifc' + layer_col.name.split('/')[1]

        layer_col_new = create_col(layer_col_name, root_col_new)

        class_col_sets = [c for c in layer_col.children]
        for class_col in class_col_sets:
            create_col_recursion(class_col.name, layer_col_new, 5, -1)

            current = float(class_col_sets.index(class_col))
            total = float(len(class_col_sets))
            percentage = round((current / total) * 100, 2)
            p = progress_bar(percentage, '#', 40)
            # print(">>> class_col progress rate: [{}]  {} % ({}/{}) / \"{}\" done.".format(p, percentage, int(current),
            #                                                                               int(total), class_col.name))

            bpy.data.collections.remove(class_col)

        current = float(layer_col_sets.index(layer_col))
        total = float(len(layer_col_sets))
        percentage = round((current / total) * 100, 2)
        p = progress_bar(percentage, '#', 40)
        # print(">>> class_col progress rate: [{}]  {} % ({}/{}) / \"{}\" done.".format(p, percentage, int(current),
        #                                                                               int(total), layer_col.name))

        objs = [o for o in layer_col.objects if o.type == 'MESH']
        for o in objs:

            # o.modifiers.
            if len(o.BIMAttributeProperties.attributes.keys()) > 0:
                print(o.BIMAttributeProperties.attributes.keys())
            create_col_recursion(o.name, layer_col_new, 5, -1)
            try:
                name_with_id = o.name + '_' + o.BIMAttributeProperties.attributes['Tag'].string_value
                o.name = name_with_id
            except:
                pass
            current = float(objs.index(o))
            total = float(len(objs))
            percentage = round((current / total) * 100, 2)
            p = progress_bar(percentage, '#', 40)
            # print(">>> objs progress rate: [{}]  {} % ({}/{}) / \"{}\" done.".format(p, percentage, int(current),
            #                                                                          int(total), o.name))

    # ------------------------------------
    # Step 2 - Complete the output, report and prompt.
    # ------------------------------------
    print("")
    print("------------------------------")
    print("--- ALL PROGRESS COMPLETED ---")
    print("------------------------------")


run_batch()
# ---
