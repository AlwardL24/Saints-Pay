from tkinter import *
from tkinter import ttk


class Window(Toplevel):
    callback = None

    def __init__(self, master, callback):
        Toplevel.__init__(self, master)

        self.title("Setup Barcode Scanner")
        self.callback = callback

        self.geometry("350x250")
        self.resizable(False, False)

        def focus():
            self.lift()
            self.focus_force()

        self.after(10, lambda: focus())

        frame = Frame(self)
        frame.pack(fill=X, padx=20, pady=20)

        label = Label(
            frame,
            text="Setup a barcode scanner, magnetic stripe reader or\n other input device to scan student IDs.",
            font=("Helvetica", 12),
        )
        label.pack(fill=X)

        label2 = Label(
            frame,
            text="Connect the device to your computer \nand scan a card to continue. \nClose this window once you're finished.",
            font=("Helvetica", 12),
        )
        label2.pack(fill=X, pady=(10, 0))

        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill=X, pady=20)

        state = Label(
            frame,
            text="Waiting for input...",
            font=("Helvetica", 12),
        )
        state.pack(fill=X)

        def detected(_):
            state.config(text="Input detected successfully")
            self.after(1000, lambda: state.config(text="Waiting for input..."))

        self.bind("<Key>", detected)

    def destroy(self) -> None:
        self.callback()

        return super().destroy()
