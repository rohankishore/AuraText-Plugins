from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QDockWidget


def markdown_new(self):
    self.mdnew.setStyleSheet("QDockWidget {background-color : #1b1b1b; color : white;}")
    self.mdnew.setMinimumWidth(400)
    self.md_widget = QTextEdit()
    self.md_widget.setReadOnly(True)
    self.md_layout = QVBoxLayout(self.md_widget)
    self.md_layout.addWidget(self.md_widget)
    self.mdnew.setWidget(self.md_widget)
    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.mdnew)

    def update():
        a = self.current_editor.text()
        self.md_widget.setMarkdown(a)

    self.current_editor.textChanged.connect(update)

def markdown_open(self, path_data):
    self.md_dock = QDockWidget("Markdown Preview")
    self.md_dock.setStyleSheet("QDockWidget {background-color : #1b1b1b; color : white;}")
    self.md_dock.setMinimumWidth(400)
    self.md_widget = QTextEdit()
    self.md_widget.setMarkdown(path_data)
    text = self.current_editor.text()
    self.md_widget.setMarkdown(text)
    self.md_widget.setReadOnly(True)
    self.md_layout = QVBoxLayout(self.md_widget)
    self.md_layout.addWidget(self.md_widget)
    self.md_dock.setWidget(self.md_widget)
    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.md_dock)

    def update():
        a = self.current_editor.text()
        self.md_widget.setMarkdown(a)

    self.current_editor.textChanged.connect(update)