from tkinter import *
from tkinter.scrolledtext import ScrolledText


class SmoothScrolledText(ScrolledText):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        master.bind(
            "<MouseWheel>",
            self.scroll,
        )
        self.bind("<MouseWheel>", self.scroll)
        self.vbar.bind("<MouseWheel>", self.scroll)

    def scroll(self, event):
        self.yview_moveto(self.yview()[0] + self.vbar.delta(0, -event.delta * 2))
        return "break"
