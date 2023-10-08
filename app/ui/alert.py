from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from typing import Callable
import os
from utils.tkinter.center import center


class Window(Toplevel):
    def __init__(
        self,
        parent,
        title,
        message,
        style="info",
        buttons: list[str] = ["OK"],
        callback: Callable[[str], None] = None,
        inputs: list[StringVar] = [],
        destroy_first: bool = True,
    ):
        Toplevel.__init__(self, parent)

        self.title(title)

        self.geometry("340x120")
        self.resizable(False, False)

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20, expand=True, fill=BOTH)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        icon = Image.open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), f"../assets/{style}.png"
            )
        )
        icon = ImageTk.PhotoImage(icon)
        icon_label = Label(frame, image=icon, height=48, width=48, bg=self["bg"])
        icon_label.image = icon  # Prevents Garbage Collection
        icon_label.grid(row=0, column=0, rowspan=2, sticky="NWSE", padx=(0, 10))

        for i, input in enumerate(inputs):
            ttk.Entry(frame, textvariable=input).grid(
                row=i + 1, column=1, sticky="NWSE", pady=(0, 5)
            )

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=1 + len(inputs), column=1, sticky="SE", pady=(10, 0))

        def button_pressed(button):
            if destroy_first:
                self.destroy()
                if callback:
                    callback(button)
            else:
                if callback:
                    callback(button)
                self.destroy()

        def button_pressed_function_generator(button):
            return lambda: button_pressed(button)

        for i, button in enumerate(buttons):
            button = ttk.Button(
                buttons_frame,
                text=button,
                command=button_pressed_function_generator(button),
            )
            button.grid(row=0, column=i, padx=(0, 10))

            if len(buttons) - 1 == i:
                button.focus_set()

        def wrap_message_label(_):
            self.message_label.config(wraplength=self.message_label.winfo_width())

            self.geometry(
                f"{self.winfo_width()}x{self.message_label.winfo_reqheight() + len(inputs) * 40 + buttons_frame.winfo_height() + 50}"
            )
            # print(self.message_label.winfo_reqheight())

        self.message_label = ttk.Label(
            frame,
            text=message,
        )
        self.message_label.grid(row=0, column=1, sticky="NWE")

        self.message_label.bind(
            "<Configure>",
            wrap_message_label,
        )

        self.bind("<Return>", lambda _: self.destroy())

        self.focus_set()

        center(self, 50, 50)

    def set_message(self, message):
        self.message_label.config(text=message)


if __name__ == "__main__":
    from ttkthemes import ThemedTk

    root = ThemedTk(theme="arc", toplevel=True)
    root.withdraw()

    Window(root, "Title", "Message")
    Window(
        root,
        "OLE Login Warning",
        "You are currently logged in as a {data['role']}. A staff account is required to show student photos and tutor groups.",
        "warning",
    )
    Window(root, "Title", "Message", "error")

    root.mainloop()
