from tkinter import *
from typing import Any, Dict, Literal, TypedDict, Union
from typing_extensions import Unpack


class EntryWithPlaceholderParams(TypedDict):
    cnf: Union[Dict[str, Any], None]
    background: str
    bd: Any
    bg: str
    border: Any
    borderwidth: Any
    cursor: Any
    disabledbackground: str
    disabledforeground: str
    exportselection: bool
    fg: str
    font: Any
    foreground: str
    highlightbackground: str
    highlightcolor: str
    highlightthickness: Any
    insertbackground: str
    insertborderwidth: Any
    insertofftime: int
    insertontime: int
    insertwidth: Any
    invalidcommand: Any
    invcmd: Any
    justify: Literal["left", "center", "right"]
    name: str
    readonlybackground: str
    relief: Any
    selectbackground: str
    selectborderwidth: Any
    selectforeground: str
    show: str
    state: Literal["normal", "disabled", "readonly"]
    takefocus: Any
    textvariable: Variable
    validate: Literal["none", "focus", "focusin", "focusout", "key", "all"]
    validatecommand: Any
    vcmd: Any
    width: int
    xscrollcommand: Any


class EntryWithPlaceholder(Entry):
    def __init__(
        self,
        master=None,
        placeholder="PLACEHOLDER",
        color="grey",
        keytyped_callback=None,
        *args,
        **kwargs: Unpack[EntryWithPlaceholderParams]
    ):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["fg"]
        self.last_known_value = None
        self.showing_placeholder = False
        self.keytyped_callback = keytyped_callback

        self.bind("<KeyRelease>", lambda _: self.placeholder_check())
        self.bind("<FocusIn>", lambda _: self.placeholder_check())
        self.bind("<Button-1>", lambda _: self.placeholder_check())

        self.put_placeholder()

    def put_placeholder(self):
        self.showing_placeholder = True
        self.insert(0, self.placeholder)
        self.icursor(0)
        self["fg"] = self.placeholder_color

    def placeholder_check(self):
        if self.showing_placeholder and self.get() != self.placeholder:
            self["fg"] = self.default_fg_color
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
