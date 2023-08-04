import sys

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QColorDialog, QWidget, QApplication, QDialog


class GetTheColor(QDialog):
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = GetTheColor()
    dialog.exec()
    sys.exit()