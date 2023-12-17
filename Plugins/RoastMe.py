import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QActionGroup, QFileSystemModel, QPixmap, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow,
    QInputDialog,
    QHBoxLayout,
    QVBoxLayout,
    QDockWidget,
    QTextEdit,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QStatusBar,
)
from auratext import Plugin
from auratext.Core.window import Window
from roastedbyai import Conversation, Style


class RoastMeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.script_edit = QLineEdit()
        self.script_edit.setFont(QFont("Consolas"))
        self.setStyleSheet("QWidget {background-color: #FFFFFF;}")
        self.script_edit.setStyleSheet(
            "QLineEdit {"
            "   border-radius: 5px;"
            "   padding: 5px;"
            "   background-color: #000000;"
            "   color: #21FC0D;"  # Color name: Electric Green
            "}"
        )

        self.text = QTextEdit()
        self.text.setFont(QFont("Consolas"))
        self.text.setReadOnly(True)
        self.text.setStyleSheet("QTextEdit {background-color: #000000;color: white; border:none;}")

        # Set up a layout for the script_edit and button
        layout = QHBoxLayout()
        layout.addWidget(self.script_edit)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove any margins

        # Set up the main layout that includes the QTextEdit and the layout with script_edit and button
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.text)
        main_layout.addLayout(layout)  # Add the layout with script_edit and button to the main layout

        self.setLayout(main_layout)

        self.quitSc = QShortcut(QKeySequence("Return"), self)
        self.quitSc.activated.connect(self.run_script)

    def run_script(self):
        convo = Conversation(Style.adult)
        script = self.script_edit.text()
        response = convo.send(script)
        self.text.append(("\n" + response))


class RoastMe(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)
        self.widget = QPlainTextEdit()

        self.window = window

        action = self.window.addAction("Show Logs")
        action.setShortcut("Alt+Shift+C")
        action.triggered.connect(
            lambda: self.run_rm() if self.widget.isHidden() else self.widget.hide()
        )

        self.tts_menu_item = QAction("Speak Selected Text", self.window)
        self.tts_menu_item.triggered.connect(self.run_rm)

        # Add the new menu item to the CodeEditor's context menu
        self.window.current_editor.context_menu.addAction("Hello", self.tts_menu_item)


    def run_rm(self):
        self.a = QDockWidget("RoastMe", self.window)
        widget = RoastMeWidget()
        self.a.setWidget(widget)
        self.a.setMinimumWidth(300)
        self.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.a)
