# ReadAloud.py
import sys

from PyQt6.QtWidgets import QMenu
from plugin_interface import MenuPluginInterface
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QColorDialog, QWidget, QApplication, QDialog

class MainApp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setWindowTitle("GetTheColor")
        self.setGeometry(180, 130, 180, 130)

    def initUI(self):
        layout = QVBoxLayout()
        self.color_label = QLabel("Selected Color: ")
        layout.addWidget(self.color_label)
        pick_color_button = QPushButton("Pick a Color")
        pick_color_button.clicked.connect(self.pickColor)
        layout.addWidget(pick_color_button)
        self.setLayout(layout)

    def pickColor(self):
        color_dialog = QColorDialog(self)
        color = color_dialog.getColor()
        if color.isValid():
            self.color_label.setText(f"Selected Color: {color.name()}")
            QApplication.clipboard().setText(color.name())
            self.color_label.setStyleSheet(f"QLabel {{ background-color: {color.name()}; color: #ffffff; }}")

class GetTheColor(MenuPluginInterface):
    def __init__(self, text_widget):
        super().__init__(text_widget)
        self.section = "Tools"

    def add_menu_items(self, context_menu: QMenu):
        talk_action = QAction("GetTheColor", context_menu)
        talk_action.triggered.connect(lambda : self.run())
        context_menu.addAction(talk_action)

    def run(self):
        app = QApplication(sys.argv)
        dialog = MainApp()
        dialog.exec()
