from tkinter import *
from tkinter import ttk
import backend.ole
import backend.transaction
import backend.operator
from datetime import datetime
import time
from utils.system_agnostic_datetime_format import sadf
import utils.system_sans_font


class Window(Toplevel):
    def __init__(
        self,
        master,
        student: backend.ole.OLE.Student,
        amount: int,
        confirmed_callback,
        canceled_callback=None,
        is_simplified_mode=False,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Confirm Transaction")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 400)}x{int(utils.system_sans_font.window_size_multiplier * 240)}"
        )
        # self.resizable(False, False)

        self.student = student
        self.amount = amount
        self.confirmed_callback = confirmed_callback

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, sticky="SE")

        self.time_now = int(time.time())

        def cancel_button_pressed():
            if canceled_callback is not None:
                canceled_callback()

            self.destroy()

        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=cancel_button_pressed,
            style="SaintsPayStyle.Simplified.TButton" if is_simplified_mode else None,
        )
        cancel_button.grid(row=0, column=0, sticky="NSEW", padx=(0, 5))

        confirm_button = ttk.Button(
            buttons_frame,
            text="Confirm",
            command=self.confirm,
            style="SaintsPayStyle.Simplified.TButton" if is_simplified_mode else None,
        )
        confirm_button.grid(row=0, column=1, sticky="NSEW", padx=(5, 0))

        confirm_button.focus_set()

        self.bind("<Return>", lambda _: self.confirm())

        if is_simplified_mode:
            cost_canvas = Canvas(
                frame,
                width=0,
                height=0,
            )
            cost_canvas.grid(row=0, column=0, columnspan=2, sticky="NSEW")

            def configure_cost_canvas():
                width = frame.winfo_width() - 5
                height = frame.winfo_height() - 10 - buttons_frame.winfo_height()

                cost_canvas.configure(
                    width=width,
                    height=height,
                )

                cost_canvas.delete("all")

                amount_as_string = str(amount)

                cost_canvas.create_text(
                    (width) / 2,
                    (height) / 2,
                    text=f"${amount_as_string[:-2]}.{amount_as_string[-2:]}",
                    angle=180,
                    anchor="center",
                    font=(
                        utils.system_sans_font.bold,
                        int(80 * utils.system_sans_font.size_multiplier),
                    ),
                )

            self.bind(
                "<Configure>",
                lambda _: configure_cost_canvas(),
            )

            configure_cost_canvas()

            return

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

        amount_as_string = str(amount)

        amount_label = ttk.Label(
            frame,
            text=f"${amount_as_string[:-2]}.{amount_as_string[-2:]}",
            style="SaintsPayStyle.L.TLabel",
        )
        amount_label.grid(row=1, column=1, sticky="NW")

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

    def confirm(self):
        print("CALLED")
        backend.transaction.new_transaction(
            student_schoolbox_id=self.student.schoolbox_id,
            amount=self.amount,
            time=self.time_now,
            operator=backend.operator.operator,
        )

        self.destroy()
        self.confirmed_callback()
