import sys
import threading

import pyttsx3
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtWidgets import QMenu, QDialog

from auratext import Plugin
from auratext.Core.AuraText import CodeEditor
from auratext.Core.window import Window

class Hi(QDialog):
    def __init__(self):
        super().__init__()

class RoastM(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)

        self.window = window

        self.me = QAction("Hi Me", self.window)
        self.me.triggered.connect(self.run_rm)

        # Add the new menu item to the CodeEditor's context menu
        self.window.current_editor.context_menu.addAction(self.me)

    def run_rm(self):
        d = Hi()
        d.exec()
