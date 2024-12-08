import sys
import threading

import pyttsx3
from PyQt6.QtGui import QKeySequence, QShortcut, QAction, QFont, QPainter, QPen, QIcon
from PyQt6.QtWidgets import QMenu, QDialog, QLabel, QDockWidget, QWidget, QVBoxLayout, QComboBox, QPushButton
from PyQt6.QtCore import QTimer, Qt

from auratext import Plugin
from auratext.Core.AuraText import CodeEditor
from auratext.Core.window import Window

class StringManipulation(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)

        self.window = window

        self.sm_menu = QMenu("&String Manipulation", self.window)
        self.case_menu = QMenu("&Case", self.window)
        self.capitalize = QAction("Capitalize", self.window)
        self.capitalize.triggered.connect(self.toUpper)
        self.lowercase = QAction("Lowercase", self.window)
        self.lowercase.triggered.connect(self.toLower)
        self.case_menu.addAction(self.capitalize)
        self.case_menu.addAction(self.lowercase)
        self.sm_menu.addMenu(self.case_menu)
        #self.sm_action.triggered.connect(self.run_rm)

        button = QPushButton("Pomodoro Timer")
        button.clicked.connect(self.run_rm)

        self.window.current_editor.context_menu.addMenu(self.sm_menu)
        #self.window.addWidget_toPlugin(button)

    def toUpper(self):
        try:
            text = str(self.window.current_editor.selectedText())
            cap_text = text.upper()
            self.window.current_editor.replaceSelectedText(cap_text)
        except Exception as e:
            print(e)

    def toLower(self):
        try:
            text = str(self.window.current_editor.selectedText())
            cap_text = text.lower()
            self.window.current_editor.replaceSelectedText(cap_text)
        except Exception as e:
            print(e)

    def run_rm(self):
        try:
            pass
        except Exception as e:
            print(e)
