from tkinter import messagebox
import pyttsx3
import threading

def rightSpeak(text):
    if text != "":
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        messagebox.showerror(
            "Text not found!",
            "Did you forget to bring your words to the party? Don't worry, just type something "
            "and let's get this conversation started!")


def speak(self):
    def speak_init():
        text = self.current_editor.text()
        rightSpeak(text)

    speak_thread = threading.Thread(target=speak_init)
    speak_thread.start()