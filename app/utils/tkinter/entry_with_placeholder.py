from tkinter import *
from tkinter import ttk


class EntryWithPlaceholder(ttk.Entry):
    def __init__(
        self,
        master=None,
        placeholder="PLACEHOLDER",
        color="grey",
        keytyped_callback=None,
        shows_right_click_menu=True,
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

        if shows_right_click_menu:
            print("Bound")
            self.bind("<Button-2>", self.show_right_click_menu)
            self.bind("<Button-3>", self.show_right_click_menu)

    def put_placeholder(self):
        self.showing_placeholder = True
        self.insert(0, self.placeholder)
        self.icursor(0)
        self.configure(style="Placeholder.TEntry")

    def placeholder_check(self):
        if self.showing_placeholder and self.get() != self.placeholder:
            self.configure(style=self.default_style)
            if (
                min(
                    max(
                        self.index(INSERT) - (len(self.get()) - len(self.placeholder)),
                        0,
                    ),
                    len(self.get()),
                )
                != 0
            ):
                self.delete(
                    0,
                    min(
                        max(
                            self.index(INSERT)
                            - (len(self.get()) - len(self.placeholder)),
                            0,
                        ),
                        len(self.get()),
                    ),
                )
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

    def show_right_click_menu(self, event):
        print("TRYING TO SHOW MENU")

        def cut():
            self.event_generate("<<Cut>>")
            self.placeholder_check()

        def copy():
            self.event_generate("<<Copy>>")
            self.placeholder_check()

        def paste():
            self.event_generate("<<Paste>>")
            self.placeholder_check()

        menu = Menu(self, tearoff=0)
        menu.add_command(label="Cut", command=cut)
        menu.add_command(label="Copy", command=copy)
        menu.add_command(label="Paste", command=paste)
        menu.add_separator()
        menu.add_command(label="Clear", command=self.clear)
        menu.tk_popup(event.x_root, event.y_root)
