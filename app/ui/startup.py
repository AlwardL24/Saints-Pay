from tkinter import *
from tkinter import ttk
from . import alert
from utils.tkinter.center import center


class Window(Toplevel):
    def __init__(self, master, quit_callback=None):
        Toplevel.__init__(self, master)
        self.title("Starting Saints Pay...")

        self.geometry("300x120")
        self.resizable(False, False)

        self.quit_callback = quit_callback

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20)

        title = ttk.Label(
            frame,
            text="Saints Pay",
            style="SaintsPayStyle.BoldXXL.TLabel",
        )
        title.pack()

        self.subtitle = ttk.Label(
            frame,
            text="Loading...",
            style="SaintsPayStyle.L.TLabel",
        )
        self.subtitle.pack()

        self.protocol("WM_DELETE_WINDOW", self.on_destroy)

        center(self, -50, -50)

    def set_loading_text(self, text):
        text = text if text else "Loading..."
        self.subtitle.configure(text=text)

    def on_destroy(self):
        if self.quit_callback is not None:
            button = ""

            def alert_callback(_button):
                nonlocal button
                button = _button

            alert.Window(
                self,
                "Quit Saints Pay",
                "Are you sure you want to quit Saints Pay?",
                style="warning",
                buttons=["Cancel", "Quit"],
                callback=alert_callback,
            ).wait_window()

            if button == "Quit":
                self.quit_callback()
