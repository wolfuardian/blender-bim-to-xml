import io
import math
import time

import xml.etree.ElementTree as Et

from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar

import sys


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.start_button = None
        self.stop_button = None
        self.progressbar = None
        self.text_edit = None

        proj_path = r'C:\Users\user\Desktop\test'
        fbx_paths = []

        demo_paths = ['C:/Users/eos/PycharmProjects/xml-editor-for-maya/resources/OCMSProject/xml_files/p220606.xml',
                      'C:/Users/eos/PycharmProjects/xml-editor-for-maya/resources/OCMSProject/xml_files/FOXCONN.xml',
                      'C:/Users/eos/PycharmProjects/xml-editor-for-maya/resources/OCMSProject/xml_files/FOXCONN_lite.xml']
        xml_string = io.open(demo_paths[1], mode='r', encoding='utf-16').read()
        root = Et.fromstring(xml_string)

        # self.task_sync_xml_nodes = TaskSyncXMLNodes()
        # self.task_sync_xml_nodes.setup(root)
        # self.task_sync_xml_nodes.execute()

        self.init_ui()

        # task_import_fbx.execute_tasks()

    def init_ui(self):
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        self.progressbar = QProgressBar()
        layout.addWidget(self.progressbar)

        self.start_button = QPushButton("Start Tasks")
        self.start_button.clicked.connect(self.task_sync_xml_nodes.execute)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Tasks")
        self.stop_button.clicked.connect(self.task_sync_xml_nodes.stop)
        layout.addWidget(self.stop_button)

        self.text_edit = QTextEdit()
        # self.text_edit.document().setMaximumBlockCount(100)
        layout.addWidget(self.text_edit)

        self.task_sync_xml_nodes.task_signals.message.connect(self.update_textedit)
        self.task_sync_xml_nodes.task_signals.progress.connect(self.update_progressbar)

    def update_textedit(self, message, color):
        color = (200, 200, 200) if color is None else color
        self.text_edit.setTextColor(QColor(*color))
        self.text_edit.append(message)

    def update_progressbar(self, current, total):
        self.progressbar.setValue(math.floor(current / total * 100))


if __name__ == "__main__":
    window = MainWindow()
    window.show()
