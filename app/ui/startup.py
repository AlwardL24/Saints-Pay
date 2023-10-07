from tkinter import *
from tkinter import ttk
import utils.system_sans_font


class Window(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title("Starting Saints Pay...")

        self.geometry("300x120")
        self.resizable(False, False)

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

    def set_loading_text(self, text):
        text = text if text else "Loading..."
        self.subtitle.configure(text=text)
