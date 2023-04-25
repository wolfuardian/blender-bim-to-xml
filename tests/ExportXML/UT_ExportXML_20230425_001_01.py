import bpy
import xml.etree.ElementTree as ET

# 創建根元素
root = ET.Element("root")

# 遍歷場景中的所有物體
for obj in bpy.context.scene.objects:
    # 創建 'Object' 元素並將其添加到根元素
    object_element = ET.SubElement(root, "Object")

    # 為 'Object' 元素添加 'type' 屬性，並將其設置為 'Device'
    object_element.set("type", "Device")

    # 將物體的名稱設置為元素的文本內容
    object_element.text = obj.name

# 將 XML 數據寫入文件
tree = ET.ElementTree(root)
tree.write("exported_objects.xml", encoding="utf-8", xml_declaration=True)
