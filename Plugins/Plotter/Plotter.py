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

__name__ = "Live Server"
__author__ = "Rohan Kishore"
__readme__ = " # Live Server "

class LiveReloadHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler that injects live reload script into HTML files"""
    
    reload_script = """
    <script>
    (function() {
        let lastCheck = Date.now();
        setInterval(async () => {
            try {
                const response = await fetch('/__livereload__?t=' + lastCheck);
                const data = await response.text();
                if (data === 'reload') {
                    location.reload();
                }
                lastCheck = Date.now();
            } catch(e) {}
        }, 500);
    })();
    </script>
    """
    
    should_reload = False
    
    def do_GET(self):
        if self.path.startswith('/__livereload__'):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            if LiveReloadHandler.should_reload:
                self.wfile.write(b'reload')
                LiveReloadHandler.should_reload = False
            else:
                self.wfile.write(b'ok')
            return
        
        # For HTML files, inject the reload script
        if self.path.endswith(('.html', '.htm')) or self.path == '/':
            try:
                # Determine the file path
                path = self.translate_path(self.path)
                
                # If it's a directory, look for index.html
                if os.path.isdir(path):
                    for index in ('index.html', 'index.htm'):
                        index_path = os.path.join(path, index)
                        if os.path.exists(index_path):
                            path = index_path
                            break
                
                if os.path.isfile(path) and path.endswith(('.html', '.htm')):
                    with open(path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                    
                    # Inject script before </body> or at end
                    if '</body>' in content:
                        content = content.replace('</body>', self.reload_script + '</body>')
                    else:
                        content += self.reload_script
                    
                    content_bytes = content.encode('utf-8')
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(content_bytes)))
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self.wfile.write(content_bytes)
                    return
            except Exception:
                pass
        
        # For non-HTML files or errors, use default handler
        super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress console logging
        pass


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

    