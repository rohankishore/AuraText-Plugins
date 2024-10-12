import sys
import threading

import pyttsx3
from PyQt6.QtGui import QKeySequence, QShortcut, QAction
from PyQt6.QtWidgets import QMenu

from auratext import Plugin
from auratext.Core.AuraText import CodeEditor
from auratext.Core.window import Window

engine = pyttsx3.init()


class TTS(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)

        self.window = window

        self.tts_menu = QMenu("&Speak")

        self.tts_menu_item1 = QAction("Selected Text", self.window)
        self.tts_menu_item1.triggered.connect(self.selected_text)
        self.tts_menu.addAction(self.tts_menu_item1)

        self.tts_menu_item2 = QAction("Whole Document", self.window)
        self.tts_menu_item2.triggered.connect(self.whole_document)
        self.tts_menu.addAction(self.tts_menu_item2)

        self.window.current_editor.context_menu.addMenu(self.tts_menu)

    def whole_document(self):
        def tts_run():
            a = self.window.current_editor.text()
            engine.say(a)
            engine.runAndWait()

        tts_thread = threading.Thread(target=tts_run)
        tts_thread.start()

    def selected_text(self):
        def tts_run():
            a = self.window.current_editor.selectedText()
            engine.say(a)
            engine.runAndWait()

        tts_thread = threading.Thread(target=tts_run)
        tts_thread.start()
