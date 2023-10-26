from tkinter import *
from tkinter import ttk
import backend.transaction
import backend.operator
from utils.date_entry import Datepicker
from . import student_search
from datetime import datetime
from utils.system_agnostic_datetime_format import sadf
import utils.system_sans_font


class Window(Toplevel):
    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
        transaction: backend.transaction.Transaction,
        callback: callable,
        is_simplified_mode=False,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Edit Transaction")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 450)}x{int(utils.system_sans_font.window_size_multiplier * 270)}"
        )
        # self.resizable(False, False)

        self.ole = ole
        self.transaction = transaction
        self.callback = callback

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="Student:", style="SaintsPayStyle.Bold.TLabel").grid(
            row=0, column=0, sticky="E", padx=(0, 10)
        )

        student_selection_frame = ttk.Frame(frame)

        selected_student_name_label = ttk.Label(
            student_selection_frame,
            text="No student selected"
            if self.transaction.student_schoolbox_id is None
            else ole.student_from_id(self.transaction.student_schoolbox_id).name,
        )
        selected_student_name_label.pack(side=LEFT, fill=BOTH, expand=True)

        student_search_window = None

        def student_selected(student):
            nonlocal student_search_window
            selected_student_name_label.configure(text=student.name)
            self.transaction.student_schoolbox_id = student.schoolbox_id
            if student_search_window is not None:
                student_search_window.destroy()
                student_search_window = None

        def student_search_button_pressed():
            nonlocal student_search_window
            student_search_window = student_search.Window(
                self,
                ole,
                title="Search for a student",
                select_command=student_selected,
            )

        student_selection_button = ttk.Button(
            student_selection_frame,
            text="Search...",
            command=student_search_button_pressed,
            state="disabled"
            if self.transaction.student_schoolbox_id is None
            else "normal",
        )
        student_selection_button.pack(side=RIGHT, padx=(10, 0))

        student_selection_frame.grid(row=0, column=1, sticky="W", pady=(0, 10))

        ttk.Label(frame, text="Amount:", style="SaintsPayStyle.Bold.TLabel").grid(
            row=1, column=0, sticky="E", padx=(0, 10)
        )

        amount_stringvar = StringVar(value=f"${transaction.amount:.2f}")

        amount_entry = ttk.Entry(
            frame,
            textvariable=amount_stringvar,
        )
        amount_entry.grid(row=1, column=1, sticky="W", pady=(0, 10))

        def amount_entry_changed(*_):
            # remove all non digits and non periods
            amount_entry_var = amount_stringvar.get()
            amount = "".join([c for c in amount_entry_var if c.isdigit() or c == "."])

            try:
                amount = float(amount)
            except ValueError:
                amount = transaction.amount

            amount_entry_var = f"${amount:.2f}"

            amount_stringvar.set(amount_entry_var)

            transaction.amount = amount

        amount_entry.bind("<FocusOut>", amount_entry_changed)
        amount_entry.bind("<Return>", lambda _: self.focus())

        ttk.Label(frame, text="Date:", style="SaintsPayStyle.Bold.TLabel").grid(
            row=2, column=0, sticky="E", padx=(0, 10)
        )

        date = datetime.fromtimestamp(transaction.time).date()
        time = datetime.fromtimestamp(transaction.time).time()

        def date_selected(date: datetime):
            transaction.time = int(datetime.combine(date, time).timestamp())

        datepicker = Datepicker(
            frame,
            dateformat=sadf("%-d/%m/%Y"),
            datevar=StringVar(value=date.strftime(sadf("%-d/%m/%Y"))),
            onselect=date_selected,
        )
        datepicker.grid(row=2, column=1, sticky="W", pady=(0, 10))

        ttk.Label(frame, text="Time:", style="SaintsPayStyle.Bold.TLabel").grid(
            row=3, column=0, sticky="E", padx=(0, 10)
        )

        time_stringvar = StringVar(value=time.strftime(sadf("%-I:%M:%S %p")))

        def time_changed(*_):
            nonlocal time

            time_string = time_stringvar.get()

            try:
                _time = datetime.strptime(time_string, sadf("%I:%M:%S %p")).time()
            except ValueError:
                _time = time

            time = _time

            time_stringvar.set(time.strftime(sadf("%-I:%M:%S %p")))

            transaction.time = int(datetime.combine(date, time).timestamp())

        time_entry = ttk.Entry(
            frame,
            textvariable=time_stringvar,
        )
        time_entry.grid(row=3, column=1, sticky="W", pady=(0, 10))

        time_entry.bind("<FocusOut>", time_changed)
        time_entry.bind("<Return>", lambda _: self.focus())

        ttk.Label(frame, text="Operator:", style="SaintsPayStyle.Bold.TLabel").grid(
            row=4, column=0, sticky="E", padx=(0, 10)
        )

        operator_stringvar = StringVar()
        operator_stringvar.set(self.transaction.operator)

        def operator_changed(*_):
            self.transaction.operator = operator_stringvar.get()

            self.after(1, operator_combobox.selection_clear)

        operator_stringvar.trace_add("write", operator_changed)

        operators = backend.operator.get_operators()

        operator_combobox = ttk.Combobox(
            frame,
            textvariable=operator_stringvar,
            values=operators,
            state="disabled" if self.transaction.operator is None else "readonly",
        )

        operator_combobox.grid(row=4, column=1, sticky="W")

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, sticky="SE")

        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=lambda: self.destroy(),
        )
        cancel_button.grid(row=0, column=0, sticky="NSEW", padx=(0, 5))

        def confirm():
            backend.transaction.edit_transaction(self.transaction)

            self.destroy()
            self.callback()

        confirm_button = ttk.Button(
            buttons_frame,
            text="Confirm",
            command=confirm,
        )
        confirm_button.grid(row=0, column=1, sticky="NSEW", padx=(5, 0))
