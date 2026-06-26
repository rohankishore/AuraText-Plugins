import os
import platform
import urllib.request
import io
import zipfile
import gzip

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from auratext import Plugin

class RustLSP(Plugin):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

        if platform.system() == "Windows":
            self.binaryPath = os.path.join(self.window.local_app_data, "bin", "rust-analyzer.exe")
        else:
            self.binaryPath = os.path.join(self.window.local_app_data, "bin", "rust-analyzer")

        if os.path.exists(self.binaryPath):
            print("INFO: Rust-analyzer already on disk, adding to global LSP list...")
            self.window.registerLSPDictEntry("rust", self.binaryPath)
        else:
            print("INFO: Loading rust-analyzer from the internet as it is not on disk...")
            QTimer.singleShot(0, self.loadFromInternet)

    def download(self, url):
        response = urllib.request.urlopen(url)
        filedata = response.read()
        response.close()
        return filedata

    def loadFromInternet(self):
        if platform.system() == "Windows":
            url = "https://github.com/rust-lang/rust-analyzer/releases/download/2026-06-22/rust-analyzer-x86_64-pc-windows-msvc.zip"
            compression = "zip"
            filename = "rust-analyzer.exe"
        elif platform.system() == "Linux":
            unamed = os.uname().machine
            url = f"https://github.com/rust-lang/rust-analyzer/releases/download/2026-06-22/rust-analyzer-{unamed}-unknown-linux-gnu.gz"
            compression = "gz"
            filename = "rust-analyzer"

        print("INFO: Downloading binary...")
        compressedData = self.download(url)
        print("INFO: Decompressing payload...")
        if compression == "zip":
            zip_bytes = io.BytesIO(compressedData)
            with zipfile.ZipFile(zip_bytes) as z:
                for name in z.namelist():
                    if name.endswith(filename):
                        binary_data = z.read(name)
                        break
                else:
                    raise RuntimeError("Binary not found in ZIP")
        elif compression == "gz":
            binary_data = gzip.decompress(compressedData)
        else:
            raise RuntimeError("Invalid compression method used")
        print("INFO: Writing rust-analyzer to disk...")
        binDir = os.path.dirname(self.binaryPath)
        os.makedirs(binDir, exist_ok=True)
        with open(self.binaryPath, "wb") as f:
            f.write(binary_data)
        if platform.system() != "Windows":
            print("INFO: Making language server executable...")
            os.chmod(self.binaryPath, 0o755)

        print("INFO: Registering rust-analyzer into global LSP dictionary...")
        self.window.registerLSPDictEntry("rust", self.binaryPath)
