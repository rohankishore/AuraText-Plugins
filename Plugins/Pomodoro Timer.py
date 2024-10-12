import sys
import threading

import pyttsx3
from PyQt6.QtGui import QKeySequence, QShortcut, QAction, QFont, QPainter, QPen
from PyQt6.QtWidgets import QMenu, QDialog, QLabel, QDockWidget, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt

from auratext import Plugin
from auratext.Core.AuraText import CodeEditor
from auratext.Core.window import Window


class PomodoroTimer(QLabel):
    def __init__(self, duration=25):
        super().__init__()
        self.duration = duration * 60  # duration in seconds
        self.time_left = self.duration
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont('Arial', 30))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)  # update every second
        self.update_display()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
        else:
            self.timer.stop()

    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.setText(f"{minutes:02d}:{seconds:02d}")
        self.update()


class PomodoroDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Pomodoro Timer", parent)
        self.init_ui()

    def init_ui(self):
        timer = PomodoroTimer(duration=25)  # 25-minute Pomodoro
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.addWidget(timer)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setWidget(content_widget)


class RoastM(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)

        self.window = window

        self.me = QAction("Pomodoro Timer", self.window)
        self.me.triggered.connect(self.run_rm)

        # Add the new menu item to the CodeEditor's context menu
        self.window.current_editor.context_menu.addAction(self.me)

    def run_rm(self):
        try:
            dock = PomodoroDock()
            self.window.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock)
        except Exception as e:
            print(e)
