from tkinter import *
from tkinter import ttk
import backend.ole
import backend.notes
import utils.system_sans_font


class Window(Toplevel):
    def __init__(
        self,
        master,
        student: backend.ole.OLE.Student,
        update_notes_callback,
        is_simplified_mode=False,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Edit Notes [{student.name}]")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 450)}x{int(utils.system_sans_font.window_size_multiplier * 200)}"
        )
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
                int(12 * utils.system_sans_font.size_multiplier),
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

        text.insert("1.0", backend.notes.get_notes_for_student(student.schoolbox_id))

        cancel_button = ttk.Button(
            frame,
            text="Cancel",
            style="SaintsPayStyle.L.TButton",
            command=lambda: self.destroy(),
        )
        cancel_button.grid(row=1, column=1, sticky="NWSE", padx=5)

        def done_button_pressed():
            backend.notes.set_notes_for_student(
                student.schoolbox_id, text.get("1.0", END).rstrip()
            )
            update_notes_callback()
            self.destroy()

        done_button = ttk.Button(
            frame,
            text="Done",
            style="SaintsPayStyle.L.TButton",
            command=done_button_pressed,
        )
        done_button.grid(row=1, column=2, sticky="NWSE", padx=(5, 0))


# from ttkthemes import ThemedTk

# root = ThemedTk(theme="arc", toplevel=True)
# root.withdraw()

# window = Window(root, backend.ole.OLE.Student(id="123", name="John Smith"), None)

# root.mainloop()
