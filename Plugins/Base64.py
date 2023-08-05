import base64
from tkinter import messagebox


def encypt(self):
    sample_string = self.selectedText()
    if sample_string != "":
        sample_string_bytes = sample_string.encode("ascii")
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_encoded = base64_bytes.decode("ascii") + "   "
        self.replaceSelectedText(base64_encoded)
    else:
        messagebox.showerror(
            "No Selection!",
            "Looks like you're taking the non-selective approach today. Select any text to encrypt.")


def decode(self):
    base64_string = self.selectedText()
    if base64_string != "":
        base64_bytes = base64_string.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("ascii") + "   "
        self.replaceSelectedText(sample_string)
    else:
        messagebox.showerror(
            "No Selection!",
            "Looks like you're taking the non-selective approach today. Select any text to decrypt.")