from tkinter import *
from tkinter import ttk
import backend.ole
import backend.blacklist
import utils.system_sans_font


class Window(Toplevel):
    def __init__(self, master, student: backend.ole.OLE.Student):
        Toplevel.__init__(self, master)
        self.title(f"Add {student.name} to Blacklist")

        self.geometry("450x200")
        self.resizable(True, True)

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.rowconfigure(0, weight=1)

        frame.columnconfigure(0, weight=1)

        entry_for_looks = ttk.Entry(frame)
        entry_for_looks.grid(row=0, column=0, columnspan=3, sticky="NWSE", pady=(0, 20))

        text = Text(
            entry_for_looks,
            font=(
                utils.system_sans_font.normal,
                12,
            ),
            bg="white",
            highlightthickness=0,
            borderwidth=0,
            wrap=WORD,
        )
        text.pack(expand=True, fill=BOTH, padx=5, pady=5)

        entry_for_looks.bind(
            "<Button-1>", lambda _: self.after(1, lambda: text.focus())
        )

        text.insert("1.0", "No reason specified")
        text.focus()
        text.tag_add("sel", "1.0", "end")

        cancel_button = ttk.Button(
            frame,
            text="Cancel",
            style="SaintsPayStyle.L.TButton",
            command=lambda: self.destroy(),
        )
        cancel_button.grid(row=1, column=1, sticky="NWSE", padx=5)

        def done_button_pressed():
            backend.blacklist.add_student_to_blacklist(
                student.schoolbox_id, text.get("1.0", END).rstrip()
            )
            self.destroy()

        done_button = ttk.Button(
            frame,
            text="Done",
            style="SaintsPayStyle.L.TButton",
            command=done_button_pressed,
        )
        done_button.grid(row=1, column=2, sticky="NWSE", padx=(5, 0))
