import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QPushButton, QMessageBox

from auratext import Plugin
from auratext.Core.window import Window

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
        
        # Check if button already exists (prevent duplicates)
        if hasattr(self.window, '_live_server_button'):
            return
        
        # Create "Go Live" button in status bar
        self.plot_action = QAction("Plot Expression")
        self.plot_action.triggered.connect(self.plot_exp)
        self.window.current_editor.context_menu.addAction(self.plot_action)
    
    def plot_exp(self):
        try:
            pass
        except Exception as e:
            print(e)

    