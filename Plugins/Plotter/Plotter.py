import os
import sys
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re

from PyQt6.QtCore import QFileSystemWatcher, QTimer, Qt
from PyQt6.QtGui import QAction, QColor, QCursor
from PyQt6.QtWidgets import (
    QPushButton, QMessageBox, QDockWidget, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFileDialog, QMenu
)
from PyQt6.Qsci import QsciScintilla

from auratext import Plugin
from auratext.Core.window import Window

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
    HAS_PLOT_LIBS = True
except ImportError as e:
    print(f"WARNING: Error importing modules: {e}")
    HAS_PLOT_LIBS = False

MATH_INDICATOR_ID = 12

__name__ = "Plotter"
__author__ = "Rohan Kishore"


class Plotter(Plugin):
    def __init__(self, window: Window) -> None:
        super().__init__(window)
        
        self.window = window
        self.plot_dock = None
        self.detected_equations = []
        
        # Context menu action for plotting
        self.plot_action = QAction("Plot Expression", self.window)
        self.plot_action.triggered.connect(self.plot_exp)
        
        # Debounce timer for highlighting to prevent lag while typing
        self.highlight_timer = QTimer(self)
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.setInterval(300)
        self.highlight_timer.timeout.connect(self.highlight_math_equations)
        
        # Setup active editor connections on tab switches
        self.window.tab_widget.currentChanged.connect(self.on_editor_changed)
        
        # Periodic check to ensure active editor is hooked up
        self.check_editor_timer = QTimer(self)
        self.check_editor_timer.timeout.connect(self.check_active_editor)
        self.check_editor_timer.start(1000)
        
        # Initialize current editor if active
        self.on_editor_changed()
 
    def check_active_editor(self):
        editor = getattr(self.window, 'current_editor', None)
        if editor and isinstance(editor, QsciScintilla):
            if not hasattr(editor, '_math_highlighter_setup'):
                self.on_editor_changed()
 
    def on_editor_changed(self):
        editor = getattr(self.window, 'current_editor', None)
        if not editor or not isinstance(editor, QsciScintilla):
            return
            
        # Initialize style settings on the editor
        self.setup_math_highlighter(editor)
        
        # Connect text changed signal for auto-highlight updates
        try:
            editor.textChanged.disconnect(self.on_text_changed)
        except:
            pass
        editor.textChanged.connect(self.on_text_changed)
        
        # Connect indicator clicks for showing the plot option
        try:
            editor.indicatorClicked.disconnect(self.on_indicator_clicked)
        except:
            pass
        editor.indicatorClicked.connect(self.on_indicator_clicked)
        
        # Update context menu text when cursor position changes
        try:
            editor.cursorPositionChanged.disconnect(self.on_cursor_position_changed)
        except:
            pass
        editor.cursorPositionChanged.connect(self.on_cursor_position_changed)
        
        # Register plot context menu action and clean up duplicates/stale entries
        if hasattr(editor, 'context_menu'):
            for act in list(editor.context_menu.actions()):
                if act.text().startswith("Plot Expression") or act.text().startswith("Plot Equation"):
                    editor.context_menu.removeAction(act)
            editor.context_menu.addAction(self.plot_action)
            
        editor._math_highlighter_setup = True
        self.highlight_math_equations()

    def on_text_changed(self):
        self.highlight_timer.start()

    def on_cursor_position_changed(self):
        self.update_context_menu_text()

    def update_context_menu_text(self):
        editor = getattr(self.window, 'current_editor', None)
        if not editor or not isinstance(editor, QsciScintilla):
            return
            
        pos = editor.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
        
        # Check if cursor is on any detected equation
        on_eq = None
        for eq in self.detected_equations:
            if eq["start"] <= pos <= eq["end"]:
                on_eq = eq
                break
                
        if on_eq:
            self.plot_action.setText(f"Plot Equation: {on_eq['expr']}")
        else:
            selected = editor.selectedText().strip()
            if selected:
                display = selected if len(selected) < 20 else selected[:17] + "..."
                self.plot_action.setText(f"Plot Expression: {display}")
            else:
                self.plot_action.setText("Plot Expression")

    def setup_math_highlighter(self, editor):
        editor.setIndicatorDrawUnder(True, MATH_INDICATOR_ID)
        editor.SendScintilla(
            QsciScintilla.SCI_INDICSETSTYLE, 
            MATH_INDICATOR_ID, 
            QsciScintilla.INDIC_ROUNDBOX
        )
        editor.SendScintilla(
            QsciScintilla.SCI_INDICSETFORE, 
            MATH_INDICATOR_ID, 
            QColor("#3a86c8")
        )
        editor.SendScintilla(
            QsciScintilla.SCI_INDICSETALPHA, 
            MATH_INDICATOR_ID, 
            50
        )

    def apply_highlight(self, start_position: int, length: int):
        editor = self.window.current_editor
        if editor and isinstance(editor, QsciScintilla):
            editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, MATH_INDICATOR_ID)
            editor.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start_position, length)
    
    def clear_highlights(self):
        editor = self.window.current_editor
        if editor and isinstance(editor, QsciScintilla):
            editor.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, MATH_INDICATOR_ID)
            editor.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, len(editor.text()))

    def find_math_spans(self, line):
        spans = []
        
        # 1. Match assignments like: y = x**2 + 5, f(x) = sin(x)
        assignment_pattern = re.compile(
            r'\b(?:[yzfgh](?:\s*\(\s*[xt]\s*\))?)\s*=\s*(?:[0-9xt\s\+\-\*\/\(\)\^\.\*]|sin|cos|tan|log|exp|sqrt|abs|pi|e)+'
        )
        for m in assignment_pattern.finditer(line):
            expr = m.group(0)
            if '=' in expr:
                rhs = expr.split('=', 1)[1].strip()
                if any(v in rhs for v in ['x', 't', 'theta', 'sin', 'cos', 'tan', 'log', 'exp', 'sqrt', 'abs']) or any(op in rhs for op in ['+', '-', '*', '/', '^']):
                    spans.append((m.start(), m.end()))
                
        # 2. Match standalone function calls like: sin(x), log(x+1)
        func_pattern = re.compile(
            r'\b(?:sin|cos|tan|log|log10|exp|sqrt|abs|sinh|cosh|tanh|arcsin|arccos|arctan)\s*\([^)]+\)'
        )
        for m in func_pattern.finditer(line):
            spans.append((m.start(), m.end()))
            
        # 3. Match standalone algebraic expressions: e.g. x**2 + 2*x + 1, 5*t - 3
        alg_pattern = re.compile(
            r'\b[xt]\s*(?:\*\*|\^|\*|\/|\+|\-)\s*(?:[0-9xt\s\+\-\*\/\(\)\^\.\*])+'
        )
        for m in alg_pattern.finditer(line):
            spans.append((m.start(), m.end()))
            
        if not spans:
            return []
            
        # Merge overlapping/adjacent spans
        spans.sort(key=lambda x: x[0])
        merged = [spans[0]]
        for current in spans[1:]:
            prev = merged[-1]
            if current[0] <= prev[1] + 1:
                merged[-1] = (prev[0], max(prev[1], current[1]))
            else:
                merged.append(current)
                
        # Clean ends
        cleaned = []
        for start, end in merged:
            span_text = line[start:end]
            stripped = span_text.strip()
            if not stripped:
                continue
            new_start = start + span_text.find(stripped)
            new_end = new_start + len(stripped)
            cleaned.append((new_start, new_end))
            
        return cleaned

    def highlight_math_equations(self):
        editor = self.window.current_editor
        if not editor or not isinstance(editor, QsciScintilla):
            return
            
        self.clear_highlights()
        text = editor.text()
        if not text:
            return
            
        lines = text.splitlines(keepends=True)
        self.detected_equations = []
        
        pos = 0
        for line_idx, line in enumerate(lines):
            clean_line = line
            comment_start = -1
            if '#' in line:
                clean_line = line.split('#', 1)[0]
                comment_start = line.find('#')
                
            spans = self.find_math_spans(clean_line)
            for start, end in spans:
                if comment_start != -1 and start >= comment_start:
                    continue
                    
                match_text = line[start:end].strip()
                if not match_text:
                    continue
                    
                lhs = ""
                rhs = match_text
                if '=' in match_text:
                    parts = match_text.split('=', 1)
                    lhs = parts[0].strip()
                    rhs = parts[1].strip()
                    
                start_pos = pos + start
                length = end - start
                
                self.detected_equations.append({
                    "start": start_pos,
                    "end": start_pos + length,
                    "line": line_idx,
                    "lhs": lhs,
                    "rhs": rhs,
                    "expr": match_text
                })
                self.apply_highlight(start_pos, length)
            pos += len(line)

    def on_indicator_clicked(self, line, index, modifiers):
        editor = self.window.current_editor
        if not editor:
            return
        pos = editor.positionFromLineIndex(line, index)
        
        clicked_eq = None
        for eq in self.detected_equations:
            if eq["start"] <= pos <= eq["end"]:
                clicked_eq = eq
                break
                
        if clicked_eq:
            self.show_plot_menu(clicked_eq)

    def show_plot_menu(self, eq):
        menu = QMenu(self.window)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #89b4fa;
                color: #11111b;
            }
        """)
        
        plot_action = QAction(f"Plot Equation: {eq['expr']}", self.window)
        plot_action.triggered.connect(lambda: self.plot_equation(eq))
        menu.addAction(plot_action)
        menu.exec(QCursor.pos())

    def plot_equation(self, eq):
        if not HAS_PLOT_LIBS:
            QMessageBox.critical(
                self.window, 
                "Missing Dependencies", 
                "Matplotlib and NumPy are required for plotting.\nPlease install them using:\npip install matplotlib numpy"
            )
            return
            
        if hasattr(self, 'plot_dock') and self.plot_dock is not None:
            try:
                self.plot_dock.show()
                self.plot_dock.raise_()
                self.plot_dock.set_equation(eq)
                return
            except:
                pass
                
        self.plot_dock = PlotDockWidget(self.window, eq, self)
        self.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.plot_dock)

    def plot_exp(self):
        try:
            editor = self.window.current_editor
            if not editor:
                return
                
            selected_text = editor.selectedText().strip()
            
            # If no selection, check if cursor is on any highlighted math equation
            if not selected_text:
                pos = editor.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
                for eq in self.detected_equations:
                    if eq["start"] <= pos <= eq["end"]:
                        self.plot_equation(eq)
                        return
                
                QMessageBox.information(self.window, "Plotter", "Please select a mathematical expression to plot or place your cursor on a highlighted equation.")
                return
            
            lhs = ""
            rhs = selected_text
            if '=' in selected_text:
                parts = selected_text.split('=', 1)
                lhs = parts[0].strip()
                rhs = parts[1].strip()
                
            eq = {
                "lhs": lhs,
                "rhs": rhs,
                "expr": selected_text
            }
            
            self.plot_equation(eq)
        except Exception as e:
            print(e)


class PlotDockWidget(QDockWidget):
    def __init__(self, parent_window, eq, parent_plugin):
        super().__init__("Plotter", parent_window)
        self.window = parent_window
        self.plugin = parent_plugin
        self.eq = eq
        
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setMinimumWidth(400)
        
        self.setStyleSheet("""
            QDockWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QDockWidget::title {
                background-color: #181825;
                padding: 6px;
                color: #cdd6f4;
                font-weight: bold;
            }
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 4px;
                color: #cdd6f4;
                padding: 4px 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
        """)
        
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(10)
        
        self.formula_label = QLabel()
        self.formula_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa; padding: 4px 0px;")
        self.layout.addWidget(self.formula_label)
        
        # Create matplotlib figure with dark background
        self.fig = Figure(figsize=(5, 4), facecolor='#1e1e2e')
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#181825')
        self.ax.tick_params(colors='#cdd6f4', labelsize=9)
        self.ax.xaxis.label.set_color('#cdd6f4')
        self.ax.yaxis.label.set_color('#cdd6f4')
        self.ax.title.set_color('#cdd6f4')
        self.ax.spines['bottom'].set_color('#45475a')
        self.ax.spines['top'].set_color('#45475a')
        self.ax.spines['left'].set_color('#45475a')
        self.ax.spines['right'].set_color('#45475a')
        self.ax.grid(True, color='#313244', linestyle='--')
        
        self.layout.addWidget(self.canvas)
        
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        controls_layout.addWidget(QLabel("Min X:"))
        self.xmin_input = QLineEdit("-10")
        self.xmin_input.setFixedWidth(55)
        controls_layout.addWidget(self.xmin_input)
        
        controls_layout.addWidget(QLabel("Max X:"))
        self.xmax_input = QLineEdit("10")
        self.xmax_input.setFixedWidth(55)
        controls_layout.addWidget(self.xmax_input)
        
        self.update_btn = QPushButton("Plot")
        self.update_btn.clicked.connect(self.replot)
        controls_layout.addWidget(self.update_btn)
        
        self.export_btn = QPushButton("Save")
        self.export_btn.clicked.connect(self.export_plot)
        self.export_btn.setStyleSheet("background-color: #45475a; color: #cdd6f4;")
        controls_layout.addWidget(self.export_btn)
        
        self.layout.addLayout(controls_layout)
        
        self.setWidget(self.main_widget)
        self.set_equation(eq)
        
    def set_equation(self, eq):
        self.eq = eq
        self.formula_label.setText(f"Formula: {eq['expr']}")
        self.replot()
        
    def replot(self):
        try:
            xmin = float(self.xmin_input.text())
            xmax = float(self.xmax_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Inputs", "X range values must be numeric.")
            return
            
        if xmin >= xmax:
            QMessageBox.warning(self, "Invalid Inputs", "Min X must be less than Max X.")
            return
            
        self.ax.clear()
        self.ax.set_facecolor('#181825')
        self.ax.grid(True, color='#313244', linestyle='--')
        self.ax.tick_params(colors='#cdd6f4', labelsize=9)
        
        x = np.linspace(xmin, xmax, 1000)
        expr = self.eq['rhs'].replace('^', '**')
        
        eval_dict = {
            'x': x,
            't': x,
            'theta': x,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'log': np.log,
            'log10': np.log10,
            'exp': np.exp,
            'sqrt': np.sqrt,
            'abs': np.abs,
            'pi': np.pi,
            'e': np.e,
            'sinh': np.sinh,
            'cosh': np.cosh,
            'tanh': np.tanh,
            'arcsin': np.arcsin,
            'arccos': np.arccos,
            'arctan': np.arctan,
            'sec': lambda val: 1.0 / np.cos(val),
            'csc': lambda val: 1.0 / np.sin(val),
            'cot': lambda val: 1.0 / np.tan(val),
            'arcsinh': np.arcsinh,
            'arccosh': np.arccosh,
            'arctanh': np.arctanh,
            'ceil': np.ceil,
            'floor': np.floor,
        }
        
        try:
            y = eval(expr, {"__builtins__": None}, eval_dict)
            if not isinstance(y, np.ndarray):
                y = np.full_like(x, y)
                
            self.ax.plot(x, y, color='#89b4fa', linewidth=2)
            self.ax.set_title(self.eq['expr'], color='#cdd6f4', fontsize=12, fontweight='bold')
            self.ax.set_xlabel('x', color='#cdd6f4')
            self.ax.set_ylabel('y', color='#cdd6f4')
        except Exception as e:
            self.ax.text(0.5, 0.5, f"Error evaluating:\n{str(e)}", 
                         color='#f38ba8', ha='center', va='center', fontsize=10, transform=self.ax.transAxes)
            self.ax.set_title("Plot Error", color='#f38ba8', fontsize=12)
            
        self.canvas.draw()
        
    def export_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Image (*.png);;JPEG Image (*.jpg)")
        if file_path:
            self.fig.savefig(file_path, facecolor='#1e1e2e', bbox_inches='tight')

    def closeEvent(self, event):
        self.plugin.plot_dock = None
        super().closeEvent(event)
