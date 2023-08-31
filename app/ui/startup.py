from tkinter import *


class Window(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title("Starting Saints Pay...")

        self.geometry("300x100")
        self.resizable(False, False)

        frame = Frame(self)
        frame.pack(padx=20, pady=20)

        title = Label(
            frame,
            text="Saints Pay",
            font=("Helvetica Bold", 24),
        )
        title.pack()

        subtitle = Label(
            frame,
            text="Loading...",
            font=("Helvetica", 12),
        )
        subtitle.pack()
