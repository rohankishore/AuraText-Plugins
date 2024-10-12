import sys
import threading

import pyttsx3
from PyQt6.QtGui import QKeySequence, QShortcut, QAction, QFont, QPainter, QPen
from PyQt6.QtWidgets import QMenu, QDialog, QLabel, QDockWidget, QWidget, QVBoxLayout, QComboBox, QPushButton
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
        self.setMinimumHeight(120)
        self.init_ui()

    def init_ui(self):
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)

        time_list = ["5", "10", "15", "20", "30", "45", "60"]
        self.timer_options = QComboBox()
        self.timer_options.addItems(time_list)
        self.timer_options.setPlaceholderText("Timer Duration (in minutes)")
        self.layout.addWidget(self.timer_options)

        self.set_button = QPushButton("Set")
        self.set_button.clicked.connect(self.set_event)
        self.layout.addWidget(self.set_button)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setWidget(content_widget)

    def closeEvent(self, event):
        # Override the close event to hide the dock instead of closing it
        event.ignore()
        self.hide()

    def set_event(self):
        try:
            duration = int(self.timer_options.currentText())
            self.timer_widget = PomodoroTimer(duration=duration)
            self.layout.addWidget(self.timer_widget)
            self.timer_options.hide()
            self.set_button.hide()
        except Exception as e:
            print(e)


class PomodoroPlugin(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)

        self.window = window

        self.me = QAction("Pomodoro Timer", self.window)
        self.me.triggered.connect(self.run_rm)

        self.window.current_editor.context_menu.addAction(self.me)

    def run_rm(self):
        try:
            dock = PomodoroDock()
            self.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        except Exception as e:
            print(e)
