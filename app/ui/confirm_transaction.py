from tkinter import *
from tkinter import ttk
import backend.ole
import backend.transaction
import backend.operator
from datetime import datetime
import time
from utils.system_agnostic_datetime_format import sadf


class Window(Toplevel):
    def __init__(
        self,
        master,
        student: backend.ole.OLE.Student,
        amount: float,
        confirmed_callback,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Confirm Transaction")

        self.geometry("400x180")
        self.resizable(False, False)

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.rowconfigure(4, weight=1)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        student_title_label = ttk.Label(
            frame,
            text=f"Student:",
            style="SaintsPayStyle.BoldL.TLabel",
        )
        student_title_label.grid(row=0, column=0, sticky="NE")

        student_name_label = ttk.Label(
            frame,
            text=f"{student.name}",
            style="SaintsPayStyle.L.TLabel",
        )
        student_name_label.grid(row=0, column=1, sticky="NW")

        amount_title_label = ttk.Label(
            frame,
            text=f"Amount:",
            style="SaintsPayStyle.BoldL.TLabel",
        )
        amount_title_label.grid(row=1, column=0, sticky="NE")

        amount_as_string = str(int(amount * 100))

        amount_label = ttk.Label(
            frame,
            text=f"${amount_as_string[:-2]}.{amount_as_string[-2:]}",
            style="SaintsPayStyle.L.TLabel",
        )
        amount_label.grid(row=1, column=1, sticky="NW")

        time_now = int(time.time())

        time_title_label = ttk.Label(
            frame,
            text=f"Time:",
            style="SaintsPayStyle.BoldL.TLabel",
        )
        time_title_label.grid(row=2, column=0, sticky="NE")

        time_label = ttk.Label(
            frame,
            text=datetime.now().strftime(sadf("%a %-d %b %Y %-I:%M:%S %p")),
            style="SaintsPayStyle.L.TLabel",
        )
        time_label.grid(row=2, column=1, sticky="NW")

        operator_title_label = ttk.Label(
            frame,
            text=f"Operator:",
            style="SaintsPayStyle.BoldL.TLabel",
        )
        operator_title_label.grid(row=3, column=0, sticky="NE")

        operator_label = ttk.Label(
            frame,
            text=backend.operator.operator,
            style="SaintsPayStyle.L.TLabel",
        )
        operator_label.grid(row=3, column=1, sticky="NW", pady=(0, 10))

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, sticky="SE")

        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=lambda: self.destroy(),
        )
        cancel_button.grid(row=0, column=0, sticky="NSEW", padx=(0, 5))

        def confirm():
            backend.transaction.new_transaction(
                student_schoolbox_id=student.schoolbox_id,
                amount=amount,
                time=time_now,
                operator=backend.operator.operator,
            )

            self.destroy()
            confirmed_callback()

        confirm_button = ttk.Button(
            buttons_frame,
            text="Confirm",
            command=confirm,
        )
        confirm_button.grid(row=0, column=1, sticky="NSEW", padx=(5, 0))

        confirm_button.focus_set()

        self.bind("<Return>", lambda _: confirm())
