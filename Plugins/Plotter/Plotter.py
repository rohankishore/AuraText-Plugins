import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt



from auratext import Plugin
from auratext.Core.window import Window


MATH_INDICATOR_ID = 12


__name__ = "Plotter"
__author__ = "Rohan Kishore"

class Plotter(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)
        
        self.window = window
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.port = 5500
        self.watcher = None
    
        
        # Create "Go Live" button in status bar
        self.plot_action = QAction("Plot Expression")
        self.plot_action.triggered.connect(self.plot_exp)
        self.window.current_editor.context_menu.addAction(self.plot_action)
    
    def plot_exp(self):
        try:
            pass
        except Exception as e:
            print(e)

    def setup_math_highlighter(self, click_handler_slot):
        editor = self.window.current_editor
        editor.setIndicatorDrawUnder(True, MATH_INDICATOR_ID)
        editor.SendScintilla(
            QsciScintilla.SCI_INDICSETSTYLE, 
            MATH_INDICATOR_ID, 
            QsciScintilla.INDIC_ROUNDBOX
        )
        
        # 3. Set highlight color and transparency
        editor.SendScintilla(
            QsciScintilla.SCI_INDICSETFORE, 
            MATH_INDICATOR_ID, 
            QColor("#3a86c8")
        )
        # Set transparency/alpha (0 to 255) for the background box fill
        editor.SendScintilla(
            QsciScintilla.SCI_INDICSETALPHA, 
            MATH_INDICATOR_ID, 
            50
        )
        
        # 4. Connect indicator click signal
        editor.indicatorClicked.connect(click_handler_slot)

    def apply_highlight(self, start_position: int, length: int):
        editor = self.window.current_editor
        editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, MATH_INDICATOR_ID)
        editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start_position, length)
    
    def clear_highlights(self):
        editor = self.window.current_editor
        editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, MATH_INDICATOR_ID)
        editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, len(editor.text()))

    def on_indicator_clicked(self, line, index, modifiers):
        editor = self.window.current_editor
        pos = editor.positionFromLineIndex(line, index)
        val = editor.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, MATH_INDICATOR_ID, pos)
        if val:
            print(f"Math equation clicked at line {line}, index {index}")

    