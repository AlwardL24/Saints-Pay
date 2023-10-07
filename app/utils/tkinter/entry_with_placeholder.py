from tkinter import *
from tkinter import ttk


class EntryWithPlaceholder(ttk.Entry):
    def __init__(
        self,
        master=None,
        placeholder="PLACEHOLDER",
        color="grey",
        keytyped_callback=None,
        *args,
        **kwargs,
    ):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.default_style = self["style"]
        self.last_known_value = None
        self.showing_placeholder = False
        self.keytyped_callback = keytyped_callback

        self.placeholder_style = ttk.Style()
        self.placeholder_style.configure(
            "Placeholder.TEntry",
            foreground=color,
        )

        self.bind("<KeyRelease>", lambda _: self.placeholder_check())
        self.bind("<FocusIn>", lambda _: self.placeholder_check())
        self.bind("<Button-1>", lambda _: self.placeholder_check())

        self.put_placeholder()

    def put_placeholder(self):
        self.showing_placeholder = True
        self.insert(0, self.placeholder)
        self.icursor(0)
        self.configure(style="Placeholder.TEntry")

    def placeholder_check(self):
        if self.showing_placeholder and self.get() != self.placeholder:
            self.configure(style=self.default_style)
            if min(max(self.index(INSERT) - 1, 0), len(self.get())) != 0:
                self.delete(0, min(max(self.index(INSERT) - 1, 0), len(self.get())))
            if min(max(self.index(INSERT), 0), len(self.get())) != len(self.get()):
                self.delete(
                    min(max(self.index(INSERT), 0), len(self.get())),
                    len(self.get()),
                )
            self.showing_placeholder = False
        elif self.showing_placeholder:
            self.icursor(0)
        elif (not self.showing_placeholder) and self.get() == "":
            self.put_placeholder()

        current_value = self.get()
        if current_value == self.placeholder:
            current_value = ""

        if current_value != self.last_known_value:
            self.last_known_value = current_value
            if self.keytyped_callback:
                self.keytyped_callback(current_value)

    def clear(self):
        self.delete(0, len(self.get()))
        self.put_placeholder()
        self.showing_placeholder = True
        self.last_known_value = ""
