# ui for creating a TransactionFilter to filter transactions by

from tkinter import *
from tkinter import ttk
import backend.transaction
import backend.operator
from utils.date_entry import Datepicker
from . import student_search
from typing import Callable, Union
from utils.system_agnostic_datetime_format import sadf


class Window(Toplevel):
    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
        filter: backend.transaction.TransactionFilter = backend.transaction.TransactionFilter(),
        callback: Union[
            Callable[[backend.transaction.TransactionFilter], None], None
        ] = None,
        is_simplified_mode=False,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Filter Transactions")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry("450x270")
        # self.resizable(False, False)

        self.filter = filter
        self.callback = callback

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=30, expand=True, fill=BOTH)

        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        ttk.Label(frame, text="Date:", style="SaintsPayStyle.Bold.TLabel").grid(
            row=0, column=0, sticky="W", columnspan=3, pady=(0, 10)
        )

        def from_start_of_checkbutton_changed():
            if from_start_of_checkbutton.instate(["selected"]):
                from_start_of.configure(state="normal")
                self.filter.from_start_of = (
                    from_start_of.current_date.date()
                    if from_start_of.current_date is not None
                    else None
                )
            else:
                from_start_of.configure(state="disabled")
                self.filter.from_start_of = None

        from_start_of_checkbutton = ttk.Checkbutton(
            frame,
            takefocus=False,
            padding=0,
            command=from_start_of_checkbutton_changed,
        )
        from_start_of_checkbutton.grid(
            row=1,
            column=0,
            sticky="W",
        )

        if self.filter.from_start_of is not None:
            from_start_of_checkbutton.state(["selected"])

        ttk.Label(frame, text="From the start of:").grid(
            row=1, column=1, sticky="E", padx=(0, 10)
        )

        def from_start_of_date_selected(_):
            self.filter.from_start_of = (
                from_start_of.current_date.date()
                if from_start_of.current_date is not None
                else None
            )

        from_start_of = Datepicker(
            frame,
            dateformat=sadf("%-d/%m/%Y"),
            state="disabled" if self.filter.from_start_of is None else "normal",
            datevar=None
            if self.filter.from_start_of is None
            else StringVar(
                value=self.filter.from_start_of.strftime(sadf("%-d/%m/%Y")),
            ),
            onselect=from_start_of_date_selected,
        )
        from_start_of.grid(row=1, column=2, sticky="W", pady=(0, 2))

        # from_start_of.bind(
        #     "<<DateEntrySelected>>",
        #     from_start_of_date_selected,
        # )

        def to_end_of_checkbutton_changed():
            if to_end_of_checkbutton.instate(["selected"]):
                to_end_of.configure(state="normal")
                self.filter.to_end_of = (
                    to_end_of.current_date.date()
                    if to_end_of.current_date is not None
                    else None
                )
            else:
                to_end_of.configure(state="disabled")
                self.filter.to_end_of = None

        to_end_of_checkbutton = ttk.Checkbutton(
            frame, takefocus=False, padding=0, command=to_end_of_checkbutton_changed
        )
        to_end_of_checkbutton.grid(row=2, column=0, sticky="W")

        if self.filter.to_end_of is not None:
            to_end_of_checkbutton.state(["selected"])

        ttk.Label(frame, text="To the end of:").grid(
            row=2, column=1, sticky="E", padx=(0, 10)
        )

        def to_end_of_date_selected(_):
            self.filter.to_end_of = (
                to_end_of.current_date.date()
                if to_end_of.current_date is not None
                else None
            )

        to_end_of = Datepicker(
            frame,
            dateformat=sadf("%-d/%m/%Y"),
            state="disabled" if self.filter.to_end_of is None else "normal",
            onselect=to_end_of_date_selected,
            datevar=None
            if self.filter.to_end_of is None
            else StringVar(
                value=self.filter.to_end_of.strftime(sadf("%-d/%m/%Y")),
            ),
        )
        to_end_of.grid(row=2, column=2, sticky="W")

        ttk.Separator(frame, orient=HORIZONTAL).grid(
            row=3, column=0, columnspan=3, sticky="EW", pady=10
        )

        selected_student_schoolbox_id = None

        def student_checkbutton_changed():
            nonlocal selected_student_schoolbox_id

            if student_checkbutton.instate(["selected"]):
                student_selection_button.configure(state="normal")
                self.filter.student_schoolbox_id = selected_student_schoolbox_id
            else:
                student_selection_button.configure(state="disabled")
                selected_student_schoolbox_id = self.filter.student_schoolbox_id
                self.filter.student_schoolbox_id = None

        student_checkbutton = ttk.Checkbutton(
            frame, takefocus=False, padding=0, command=student_checkbutton_changed
        )
        student_checkbutton.grid(row=4, column=0, sticky="W")

        if self.filter.student_schoolbox_id is not None:
            student_checkbutton.state(["selected"])

        ttk.Label(frame, text="Student:").grid(
            row=4, column=1, sticky="E", padx=(0, 10)
        )

        student_selection_frame = ttk.Frame(frame)

        selected_student_name_label = ttk.Label(
            student_selection_frame,
            text="No student selected"
            if self.filter.student_schoolbox_id is None
            else ole.student_from_id(self.filter.student_schoolbox_id).name,
        )
        selected_student_name_label.pack(side=LEFT, fill=BOTH, expand=True)

        student_search_window = None

        def student_selected(student):
            nonlocal student_search_window
            selected_student_name_label.configure(text=student.name)
            self.filter.student_schoolbox_id = student.schoolbox_id
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
            state="disabled" if self.filter.student_schoolbox_id is None else "normal",
        )
        student_selection_button.pack(side=RIGHT, padx=(10, 0))

        student_selection_frame.grid(row=4, column=2, sticky="W", pady=(0, 2))

        def operator_checkbutton_changed():
            if operator_checkbutton.instate(["selected"]):
                operator_combobox.configure(state="readonly")
                self.filter.operator = operator_stringvar.get()
            else:
                operator_combobox.configure(state="disabled")
                self.filter.operator = None

        operator_checkbutton = ttk.Checkbutton(
            frame, takefocus=False, padding=0, command=operator_checkbutton_changed
        )
        operator_checkbutton.grid(row=5, column=0, sticky="W")

        if self.filter.operator is not None:
            operator_checkbutton.state(["selected"])

        ttk.Label(frame, text="Made by operator:").grid(
            row=5, column=1, sticky="E", padx=(0, 10)
        )

        # combo box for selecting the operator, use the current operator as default and show all operators from backend.operator.get_operators()
        operator_stringvar = StringVar()
        operator_stringvar.set(
            backend.operator.operator
            if self.filter.operator is None
            else self.filter.operator
        )

        def operator_changed(*_):
            self.filter.operator = operator_stringvar.get()

            self.after(1, operator_combobox.selection_clear)

        operator_stringvar.trace_add("write", operator_changed)

        operators = backend.operator.get_operators()

        operator_combobox = ttk.Combobox(
            frame,
            textvariable=operator_stringvar,
            values=operators,
            state="disabled" if self.filter.operator is None else "readonly",
        )

        operator_combobox.grid(row=5, column=2, sticky="W")

        ttk.Separator(frame, orient=HORIZONTAL).grid(
            row=6, column=0, columnspan=3, sticky="EW", pady=10
        )

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=7, column=0, columnspan=3, sticky="E")

        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=self.destroy)
        cancel_button.grid(row=0, column=0, padx=(0, 5))

        def ok_button_pressed():
            if self.callback is not None:
                self.callback(self.filter)

            self.destroy()

        ok_button = ttk.Button(buttons_frame, text="OK", command=ok_button_pressed)
        ok_button.grid(row=0, column=1, padx=(0, 5))
