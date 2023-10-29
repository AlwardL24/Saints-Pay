from tkinter import *
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from tkscrolledframe import ScrolledFrame
import backend.transaction
import backend.operator
from utils.date_entry import Datepicker
from sys import platform
from . import transaction_filter, alert
import datetime
from typing import Callable, Union
import xlsxwriter
from utils.system_agnostic_datetime_format import sadf
import utils.system_sans_font


class Window(Toplevel):
    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
        transactions: list[backend.transaction.Transaction] = [],
        sort_transactions_by_attribute: str = "STUDENT_LAST",
        sort_transactions_ascending: bool = True,
        is_simplified_mode=False,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Export Transactions")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 380)}x{int(utils.system_sans_font.window_size_multiplier * 470)}"
        )
        # self.resizable(False, False)

        self.ole = ole

        self.transactions = transactions
        self.sort_transactions_by_attribute = sort_transactions_by_attribute
        self.sort_transactions_ascending = sort_transactions_ascending

        self.filter = backend.transaction.TransactionFilter()

        self.date_format = "d/mm/yy"

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(15, weight=1)

        _s = "s"
        _blank = ""

        export_descriptor_label = ttk.Label(
            frame,
            text=f"Export {f'{len(self.transactions)} selected transaction{_s if len(self.transactions) != 1 else _blank}' if len(self.transactions) > 0 else self.filter.user_readable_string(ole)}",
            style="SaintsPayStyle.Bold.TLabel",
        )
        export_descriptor_label.grid(
            row=0, column=0, columnspan=2, sticky="W", pady=(0, 10)
        )

        def filter_changed(filter):
            self.filter = filter

            export_descriptor_label.configure(
                text=f"Export {f'{len(self.transactions)} selected transaction{_s if len(self.transactions) != 1 else _blank}' if len(self.transactions) > 0 else self.filter.user_readable_string(ole)}",
            )

        def filter_button_pressed():
            (
                lambda: transaction_filter.Window(
                    self.master, self.ole, self.filter, filter_changed
                )
            )()

        if len(self.transactions) <= 0:
            ttk.Button(
                frame,
                text="Filter...",
                command=filter_button_pressed,
            ).grid(row=0, column=1, sticky="E", pady=(0, 10))

        sort_by_frame = ttk.Frame(frame)
        sort_by_frame.grid(row=1, column=0, columnspan=2, sticky="W", pady=(0, 10))

        ttk.Label(sort_by_frame, text="Sort transactions by:").grid(
            row=0, column=0, sticky="W", padx=(0, 10)
        )

        sort_by_strings = {
            ("STUDENT", True): "Student First Name (A-Z)",
            ("STUDENT", False): "Student First Name (Z-A)",
            ("STUDENT_LAST", True): "Student Last Name (A-Z)",
            ("STUDENT_LAST", False): "Student Last Name (Z-A)",
            ("amount", True): "Amount (Low-High)",
            ("amount", False): "Amount (High-Low)",
            ("time", True): "Time (Old-New)",
            ("time", False): "Time (New-Old)",
            ("operator", True): "Operator Name (A-Z)",
            ("operator", False): "Operator Name (Z-A)",
        }

        sort_by_stringvar = StringVar()
        sort_by_stringvar.set(
            sort_by_strings[
                (self.sort_transactions_by_attribute, self.sort_transactions_ascending)
            ]
        )

        def sort_by_changed(*_):
            sort_by = sort_by_stringvar.get()

            for (attribute, ascending), string in sort_by_strings.items():
                if string == sort_by:
                    self.sort_transactions_by_attribute = attribute
                    self.sort_transactions_ascending = ascending
                    break

            self.after(1, sort_by_combobox.selection_clear)

        sort_by_stringvar.trace_add("write", sort_by_changed)

        sort_bys = list(sort_by_strings.values())

        sort_by_combobox = ttk.Combobox(
            sort_by_frame,
            textvariable=sort_by_stringvar,
            values=sort_bys,
            state="readonly",
            width=30,
        )
        sort_by_combobox.grid(row=0, column=1, sticky="W")

        ttk.Label(
            frame, text="Spreadsheet Columns:", style="SaintsPayStyle.Bold.TLabel"
        ).grid(row=2, column=0, columnspan=2, sticky="W", padx=(0, 10))

        self.show_column_student_full_name = BooleanVar(value=True)

        ttk.Checkbutton(
            frame,
            text="Student Full Name",
            variable=self.show_column_student_full_name,
        ).grid(row=3, column=0, columnspan=2, sticky="W")

        self.show_column_student_first_name = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Student First Name",
            variable=self.show_column_student_first_name,
        ).grid(row=4, column=0, columnspan=2, sticky="W")

        self.show_column_student_last_name = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Student Last Name",
            variable=self.show_column_student_last_name,
        ).grid(row=5, column=0, columnspan=2, sticky="W")

        self.show_column_student_username = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Student Username",
            variable=self.show_column_student_username,
        ).grid(row=6, column=0, columnspan=2, sticky="W")

        self.show_column_student_email = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Student Email",
            variable=self.show_column_student_email,
        ).grid(row=7, column=0, columnspan=2, sticky="W")

        self.show_column_student_year_level = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Student Year Level",
            variable=self.show_column_student_year_level,
        ).grid(row=8, column=0, columnspan=2, sticky="W")

        self.show_column_student_tutor_group = BooleanVar(value=True)

        ttk.Checkbutton(
            frame,
            text="Student Tutor Group",
            variable=self.show_column_student_tutor_group,
        ).grid(row=9, column=0, columnspan=2, sticky="W")

        self.show_column_amount = BooleanVar(value=True)

        ttk.Checkbutton(
            frame,
            text="Amount",
            variable=self.show_column_amount,
        ).grid(row=10, column=0, columnspan=2, sticky="W")

        self.show_column_date = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Date",
            variable=self.show_column_date,
        ).grid(row=11, column=0, columnspan=2, sticky="W")

        self.show_column_time = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Time",
            variable=self.show_column_time,
        ).grid(row=12, column=0, columnspan=2, sticky="W")

        self.show_column_operator_name = BooleanVar(value=False)

        ttk.Checkbutton(
            frame,
            text="Operator Name",
            variable=self.show_column_operator_name,
        ).grid(row=13, column=0, columnspan=2, sticky="W", pady=(0, 10))

        date_format_frame = ttk.Frame(frame)
        date_format_frame.grid(row=14, column=0, columnspan=2, sticky="W", pady=(0, 10))

        ttk.Label(date_format_frame, text="Date Format:").grid(
            row=0, column=0, sticky="W", padx=(0, 10)
        )

        date_format_strings = {  # Excel date formats, not datetime.strftime formats
            "14/03/23": "d/mm/yy",
            "14/03/2023": "d/mm/yyyy",
            "Wed 14 Mar 2023": "[$-en-NZ]ddd d mmm yyyy",
        }

        date_format_stringvar = StringVar()
        date_format_stringvar.set("14/03/23")

        def date_format_changed(*_):
            date_format = date_format_stringvar.get()

            self.date_format = date_format_strings[date_format]

            self.after(1, date_format_combobox.selection_clear)

        date_format_stringvar.trace_add("write", date_format_changed)

        date_formats = list(date_format_strings.keys())

        date_format_combobox = ttk.Combobox(
            date_format_frame,
            textvariable=date_format_stringvar,
            values=date_formats,
            state="readonly",
        )
        date_format_combobox.grid(row=0, column=1, sticky="W")

        ttk.Button(
            frame,
            text="Export",
            command=self.export_button_pressed,
        ).grid(row=15, column=1, sticky="ES")

    def export_button_pressed(self):
        if len(self.transactions) <= 0:
            self.transactions = backend.transaction.get_transactions_filtered(
                self.filter
            )

        self.export_transactions(
            self.ole,
            self.transactions,
            self.sort_transactions_by_attribute,
            self.sort_transactions_ascending,
            self.date_format,
            self.show_column_student_full_name.get(),
            self.show_column_student_first_name.get(),
            self.show_column_student_last_name.get(),
            self.show_column_student_username.get(),
            self.show_column_student_email.get(),
            self.show_column_student_year_level.get(),
            self.show_column_student_tutor_group.get(),
            self.show_column_amount.get(),
            self.show_column_date.get(),
            self.show_column_time.get(),
            self.show_column_operator_name.get(),
        )

    @staticmethod
    def export_transactions(
        ole: backend.ole.OLE,
        transactions: list[backend.transaction.Transaction],
        sort_transactions_by_attribute: str = "STUDENT_LAST",
        sort_transactions_ascending: bool = True,
        date_format: str = "d/mm/yy",
        show_column_date: bool = True,
        show_column_student_number: bool = True,
        show_column_student_full_name: bool = True,
        show_column_student_first_name: bool = False,
        show_column_student_last_name: bool = False,
        show_column_student_username: bool = False,
        show_column_student_email: bool = False,
        show_column_student_year_level: bool = False,
        show_column_amount: bool = True,
        show_column_student_tutor_group: bool = True,
        show_column_time: bool = False,
        show_column_operator_name: bool = False,
        filename: str = None,
    ):
        if sort_transactions_by_attribute is not None:
            if sort_transactions_by_attribute == "STUDENT":
                transactions.sort(
                    key=lambda transaction: ole.student_from_id(
                        transaction.student_schoolbox_id
                    ).name,
                    reverse=not sort_transactions_ascending,
                )
            elif sort_transactions_by_attribute == "STUDENT_LAST":
                transactions.sort(
                    key=lambda transaction: ole.student_from_id(
                        transaction.student_schoolbox_id
                    ).name.split(" ")[-1],
                    reverse=not sort_transactions_ascending,
                )
            else:
                transactions.sort(
                    key=lambda transaction: getattr(
                        transaction, sort_transactions_by_attribute
                    ),
                    reverse=not sort_transactions_ascending,
                )

        filename = asksaveasfilename(
            initialfile=filename
            or f"Transactions-{datetime.datetime.now().strftime(sadf('%-I-%M-%p-%-d-%m-%y'))}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel Spreadsheet", "*.xlsx")],
        )

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        bold = workbook.add_format({"bold": True})
        currency = workbook.add_format({"num_format": "$#,##0.00"})
        date = workbook.add_format({"num_format": date_format})
        time = workbook.add_format({"num_format": "[$-en-NZ]h:mm:ss AM/PM"})

        columns = []

        if show_column_date:
            columns.append("Date")
        if show_column_student_number:
            columns.append("Student Number")
        if show_column_student_full_name:
            columns.append("Student Full Name")
        if show_column_student_first_name:
            columns.append("Student First Name")
        if show_column_student_last_name:
            columns.append("Student Last Name")
        if show_column_student_username:
            columns.append("Student Username")
        if show_column_student_email:
            columns.append("Student Email")
        if show_column_student_year_level:
            columns.append("Student Year Level")
        if show_column_amount:
            columns.append("Amount")
        if show_column_student_tutor_group:
            columns.append("Student Tutor Group")
        if show_column_time:
            columns.append("Time")
        if show_column_operator_name:
            columns.append("Operator Name")

        for col, column in enumerate(columns):
            worksheet.write(0, col, column, bold)

        for row, transaction in enumerate(transactions):
            row = row + 1
            for col, column in enumerate(columns):
                if column == "Student Full Name":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(transaction.student_schoolbox_id).name,
                    )
                elif column == "Student Number":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(transaction.student_schoolbox_id).id,
                    )
                elif column == "Student First Name":
                    worksheet.write(
                        row,
                        col,
                        " ".join(
                            ole.student_from_id(
                                transaction.student_schoolbox_id
                            ).name.split(" ")[:-1]
                        ),
                    )
                elif column == "Student Last Name":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(
                            transaction.student_schoolbox_id
                        ).name.split(" ")[-1],
                    )
                elif column == "Student Username":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(transaction.student_schoolbox_id).username,
                    )
                elif column == "Student Email":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(transaction.student_schoolbox_id).email,
                    )
                elif column == "Student Year Level":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(transaction.student_schoolbox_id).year,
                    )
                elif column == "Student Tutor Group":
                    worksheet.write(
                        row,
                        col,
                        ole.student_from_id(
                            transaction.student_schoolbox_id
                        ).tutor.split(" - ")[0]
                        if ole.student_from_id(transaction.student_schoolbox_id).tutor
                        is not None
                        else "",
                    )
                elif column == "Amount":
                    worksheet.write(row, col, transaction.amount, currency)
                elif column == "Date":
                    worksheet.write_datetime(
                        row,
                        col,
                        datetime.datetime.fromtimestamp(transaction.time).date(),
                        date,
                    )
                elif column == "Time":
                    worksheet.write(
                        row,
                        col,
                        datetime.datetime.fromtimestamp(transaction.time),
                        time,
                    )
                elif column == "Operator Name":
                    worksheet.write(row, col, transaction.operator)

        worksheet.autofit()

        if date_format == "[$-en-NZ]ddd d mmm yyyy":
            worksheet.set_column(
                [i for i, x in enumerate(columns) if x == "Date"][0],
                [i for i, x in enumerate(columns) if x == "Date"][0],
                16,
            )

        workbook.close()
