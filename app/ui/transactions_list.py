from tkinter import *
from tkinter import ttk
from tkscrolledframe import ScrolledFrame
import backend.transaction
import backend.operator
from utils.date_entry import Datepicker
from sys import platform
from . import transaction_filter, alert, export_transactions, edit_transaction
import datetime
from typing import Callable, Union
from utils.system_agnostic_datetime_format import sadf


class Window(Toplevel):
    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
        filter: backend.transaction.TransactionFilter = backend.transaction.TransactionFilter(),
        is_simplified_mode=False,
    ):
        Toplevel.__init__(self, master)
        self.title(f"Transactions")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry("700x400")
        # self.resizable(False, False)

        self.filter = filter
        self.ole = ole

        self.transactions = []
        self.sort_transactions_by_attribute = "STUDENT"
        self.sort_transactions_ascending = True

        self.selected_transactions: list[str] = []

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

        filter_descriptor_label = ttk.Label(
            frame,
            text=f"Showing {filter.user_readable_string(ole)}",
            style="SaintsPayStyle.BoldL.TLabel",
        )
        filter_descriptor_label.grid(
            row=0, column=0, columnspan=2, sticky="W", pady=(0, 10)
        )

        def filter_changed(filter):
            self.filter = filter

            filter_descriptor_label.configure(
                text=f"Showing {self.filter.user_readable_string(self.ole)}"
            )

            self.show_transactions()

        def filter_button_pressed():
            (
                lambda: transaction_filter.Window(
                    self.master,
                    self.ole,
                    self.filter,
                    filter_changed,
                    is_simplified_mode=is_simplified_mode,
                )
            )()

        ttk.Button(
            frame,
            text="Filter...",
            command=filter_button_pressed,
        ).grid(row=0, column=1, sticky="E")

        ttk.Separator(
            frame,
            orient=HORIZONTAL,
        ).grid(row=1, column=0, columnspan=2, sticky="WE", pady=10)

        self.selection_description_label = ttk.Label(
            frame,
            text="0 transactions selected",
        )
        self.selection_description_label.grid(row=2, column=0, sticky="W")

        action_buttons_frame = ttk.Frame(frame)
        action_buttons_frame.grid(row=2, column=1, sticky="E")

        self.edit_button = ttk.Button(
            action_buttons_frame,
            text="Edit",
            state=DISABLED,
            command=lambda: edit_transaction.Window(
                self.master,
                self.ole,
                self.selected_transactions_objects[0],
                lambda: self.show_transactions(),
                is_simplified_mode=is_simplified_mode,
            ),
        )
        self.edit_button.grid(row=0, column=0, sticky="E", padx=(0, 10))

        self.export_button = ttk.Button(
            action_buttons_frame,
            text="Export to Excel",
            state=DISABLED,
            command=lambda: export_transactions.Window(
                self.master,
                self.ole,
                self.selected_transactions_objects,
                self.sort_transactions_by_attribute,
                self.sort_transactions_ascending,
                is_simplified_mode=is_simplified_mode,
            ),
        )
        self.export_button.grid(row=0, column=1, sticky="E", padx=(0, 10))

        def delete_button_pressed():
            def callback(button):
                if button == "Delete":
                    backend.transaction.delete_transactions_with_ids(
                        self.selected_transactions
                    )
                    self.selected_transactions = []
                    self.show_transactions()
                    self.show_selection()

            alert.Window(
                self,
                "Delete Transactions",
                f"Are you sure you want to delete {len(self.selected_transactions)} transaction{'s' if len(self.selected_transactions) != 1 else ''}?",
                buttons=["Cancel", "Delete"],
                callback=callback,
                topmost=is_simplified_mode,
            )

        self.delete_button = ttk.Button(
            action_buttons_frame,
            text="Delete",
            state=DISABLED,
            command=delete_button_pressed,
        )
        self.delete_button.grid(row=0, column=2, sticky="E")

        ttk.Separator(
            frame,
            orient=HORIZONTAL,
        ).grid(row=3, column=0, columnspan=2, sticky="WE", pady=10)

        table_frame_scrolled = ScrolledFrame(frame, scrollbars="vertical", use_ttk=True)
        table_frame_scrolled.grid(row=4, column=0, columnspan=2, sticky="NWSE")

        table_frame_scrolled.bind_scroll_wheel(self)

        self.table_frame = table_frame_scrolled.display_widget(
            ttk.Frame, fit_width=True
        )

        self.table_frame.columnconfigure(0, minsize=40)
        self.table_frame.columnconfigure(1, weight=3)
        self.table_frame.columnconfigure(2, weight=1)
        self.table_frame.columnconfigure(3, weight=1)
        self.table_frame.columnconfigure(4, weight=2)

        self.select_all_checkbutton_variable = IntVar(
            value=0
        )  # 0 = unchecked, 1 = checked, 2 = partially checked

        def select_all_checkbutton_clicked():
            if len(self.selected_transactions) == len(self.transactions):
                self.selected_transactions = []
                self.select_all_checkbutton_variable.set(0)
            else:
                self.selected_transactions = [
                    transaction.id for transaction in self.transactions
                ]
                self.select_all_checkbutton_variable.set(1)

            self.selection_description_label.configure(
                text=f"{len(self.selected_transactions)} transaction{'s' if len(self.selected_transactions) != 1 else ''} selected"
            )

            if len(self.selected_transactions) == 0:
                self.edit_button.configure(state=DISABLED)
                self.export_button.configure(state=DISABLED)
                self.delete_button.configure(state=DISABLED)
            elif len(self.selected_transactions) == 1:
                self.edit_button.configure(state=NORMAL)
                self.export_button.configure(state=NORMAL)
                self.delete_button.configure(state=NORMAL)
            else:
                self.edit_button.configure(state=DISABLED)
                self.export_button.configure(state=NORMAL)
                self.delete_button.configure(state=NORMAL)

            self.show_transactions()

        ttk.Checkbutton(
            self.table_frame,
            command=select_all_checkbutton_clicked,
            variable=self.select_all_checkbutton_variable,
            onvalue=1,
            offvalue=0,
        ).grid(row=0, column=0, sticky="W", padx=(10, 0))

        student_header_frame = ttk.Frame(self.table_frame)
        student_header_frame.grid(row=0, column=1, sticky="WE")

        student_header_frame.columnconfigure(1, weight=1)

        ttk.Separator(student_header_frame, orient=VERTICAL).grid(
            row=0, column=0, sticky="NS", padx=10
        )

        ttk.Label(
            student_header_frame, text="Student", style="SaintsPayStyle.BoldL.TLabel"
        ).grid(row=0, column=1, sticky="W")

        def student_sort_button_pressed():
            if self.sort_transactions_by_attribute == "STUDENT":
                self.sort_transactions_ascending = not self.sort_transactions_ascending
            else:
                self.sort_transactions_by_attribute = "STUDENT"
                self.sort_transactions_ascending = True

            self.show_transactions()

        self.student_sort_button = Button(
            student_header_frame,
            text="•",  # • when sorting is inactive, ▲ when sorting is ascending, ▼ when sorting is descending
            command=student_sort_button_pressed,
            relief=FLAT,
            borderwidth=0,
            bg=self["bg"],
        )
        self.student_sort_button.grid(row=0, column=2)

        amount_header_frame = ttk.Frame(self.table_frame)
        amount_header_frame.grid(row=0, column=2, sticky="WE")

        amount_header_frame.columnconfigure(1, weight=1)

        ttk.Separator(amount_header_frame, orient=VERTICAL).grid(
            row=0, column=0, sticky="NS", padx=10
        )

        ttk.Label(
            amount_header_frame, text="Amount", style="SaintsPayStyle.BoldL.TLabel"
        ).grid(row=0, column=1, sticky="W")

        def amount_sort_button_pressed():
            if self.sort_transactions_by_attribute == "amount":
                self.sort_transactions_ascending = not self.sort_transactions_ascending
            else:
                self.sort_transactions_by_attribute = "amount"
                self.sort_transactions_ascending = True

            self.show_transactions()

        self.amount_sort_button = Button(
            amount_header_frame,
            text="•",  # • when sorting is inactive, ▲ when sorting is ascending, ▼ when sorting is descending
            command=amount_sort_button_pressed,
            relief=FLAT,
            borderwidth=0,
            bg=self["bg"],
        )
        self.amount_sort_button.grid(row=0, column=2)

        time_header_frame = ttk.Frame(self.table_frame)
        time_header_frame.grid(row=0, column=3, sticky="WE")

        time_header_frame.columnconfigure(1, weight=1)

        ttk.Separator(time_header_frame, orient=VERTICAL).grid(
            row=0, column=0, sticky="NS", padx=10
        )

        ttk.Label(
            time_header_frame, text="Time", style="SaintsPayStyle.BoldL.TLabel"
        ).grid(row=0, column=1, sticky="W")

        def time_sort_button_pressed():
            if self.sort_transactions_by_attribute == "time":
                self.sort_transactions_ascending = not self.sort_transactions_ascending
            else:
                self.sort_transactions_by_attribute = "time"
                self.sort_transactions_ascending = True

            self.show_transactions()

        self.time_sort_button = Button(
            time_header_frame,
            text="•",  # • when sorting is inactive, ▲ when sorting is ascending, ▼ when sorting is descending
            command=time_sort_button_pressed,
            relief=FLAT,
            borderwidth=0,
            bg=self["bg"],
        )
        self.time_sort_button.grid(row=0, column=2)

        operator_header_frame = ttk.Frame(self.table_frame)
        operator_header_frame.grid(row=0, column=4, sticky="WE")

        operator_header_frame.columnconfigure(1, weight=1)

        ttk.Separator(operator_header_frame, orient=VERTICAL).grid(
            row=0, column=0, sticky="NS", padx=10
        )

        ttk.Label(
            operator_header_frame, text="Operator", style="SaintsPayStyle.BoldL.TLabel"
        ).grid(row=0, column=1, sticky="W")

        def operator_sort_button_pressed():
            if self.sort_transactions_by_attribute == "operator":
                self.sort_transactions_ascending = not self.sort_transactions_ascending
            else:
                self.sort_transactions_by_attribute = "operator"
                self.sort_transactions_ascending = True

            self.show_transactions()

        self.operator_sort_button = Button(
            operator_header_frame,
            text="•",  # • when sorting is inactive, ▲ when sorting is ascending, ▼ when sorting is descending
            command=operator_sort_button_pressed,
            relief=FLAT,
            borderwidth=0,
            bg=self["bg"],
        )
        self.operator_sort_button.grid(row=0, column=2)

        ttk.Separator(
            self.table_frame,
            orient=HORIZONTAL,
        ).grid(row=1, column=0, columnspan=5, sticky="WE")

        self.show_transactions()

    @property
    def selected_transactions_objects(self):
        return [
            transaction
            for transaction in self.transactions
            if transaction.id in self.selected_transactions
        ]

    def get_all_table_widgets_with_tag(
        self, tag: str
    ) -> list:  # Only searches one level deep
        widgets = []

        for widget in self.table_frame.winfo_children():
            if tag in widget.bindtags():
                widgets.append(widget)

        return widgets

    def selection_checkbutton_clicked(self, transaction_id):
        if transaction_id in self.selected_transactions:
            self.selected_transactions.remove(transaction_id)
        else:
            self.selected_transactions.append(transaction_id)

        self.show_selection()

    def show_selection(self):
        self.selection_description_label.configure(
            text=f"{len(self.selected_transactions)} transaction{'s' if len(self.selected_transactions) != 1 else ''} selected"
        )

        if len(self.selected_transactions) == 0:
            self.edit_button.configure(state=DISABLED)
            self.export_button.configure(state=DISABLED)
            self.delete_button.configure(state=DISABLED)
        elif len(self.selected_transactions) == 1:
            self.edit_button.configure(state=NORMAL)
            self.export_button.configure(state=NORMAL)
            self.delete_button.configure(state=NORMAL)
        else:
            self.edit_button.configure(state=DISABLED)
            self.export_button.configure(state=NORMAL)
            self.delete_button.configure(state=NORMAL)

        if len(self.selected_transactions) == len(self.transactions):
            self.select_all_checkbutton_variable.set(1)
        elif len(self.selected_transactions) == 0:
            self.select_all_checkbutton_variable.set(0)
        else:
            self.select_all_checkbutton_variable.set(1)

    def selection_checkbutton_clicked_function_generator(self, transaction_id):
        return lambda: self.selection_checkbutton_clicked(transaction_id)

    def show_transactions(self):
        self.transactions = backend.transaction.get_transactions_filtered(self.filter)

        if self.sort_transactions_by_attribute is not None:
            if self.sort_transactions_by_attribute == "STUDENT":
                self.transactions.sort(
                    key=lambda transaction: self.ole.student_from_id(
                        transaction.student_schoolbox_id
                    ).name
                    or "",
                    reverse=not self.sort_transactions_ascending,
                )
            else:
                self.transactions.sort(
                    key=lambda transaction: getattr(
                        transaction, self.sort_transactions_by_attribute
                    ),
                    reverse=not self.sort_transactions_ascending,
                )

            sort_buttons = {
                "STUDENT": self.student_sort_button,
                "amount": self.amount_sort_button,
                "time": self.time_sort_button,
                "operator": self.operator_sort_button,
            }

            sort_button_text = "▲" if self.sort_transactions_ascending else "▼"

            for attribute, button in sort_buttons.items():
                if attribute == self.sort_transactions_by_attribute:
                    button.configure(text=sort_button_text)
                else:
                    button.configure(text="•")

        for widget in self.get_all_table_widgets_with_tag("transaction"):
            widget.destroy()

        for i, transaction in enumerate(self.transactions):
            i = i * 2 + 2

            checkbutton = ttk.Checkbutton(
                self.table_frame,
                command=self.selection_checkbutton_clicked_function_generator(
                    transaction.id
                ),
            )
            checkbutton.grid(row=i, column=0, sticky="W", padx=(10, 0))
            checkbutton.bindtags(
                (
                    "transaction",
                    "transaction_checkbutton",
                    f"transaction_{transaction.id}",
                )
                + checkbutton.bindtags()
            )

            if transaction.id in self.selected_transactions:
                checkbutton.state(["selected"])

            student_label = ttk.Label(
                self.table_frame,
                text=self.ole.student_from_id(transaction.student_schoolbox_id).name,
                style="SaintsPayStyle.L.TLabel",
            )
            student_label.grid(row=i, column=1, sticky="W", padx=(10, 0))
            student_label.bindtags(
                (
                    "transaction",
                    "transaction_student_label",
                    f"transaction_{transaction.id}",
                )
                + student_label.bindtags()
            )

            amount_label = ttk.Label(
                self.table_frame,
                text=f"${transaction.amount:.2f}",
                style="SaintsPayStyle.L.TLabel",
            )
            amount_label.grid(row=i, column=2, sticky="W", padx=(10, 0))
            amount_label.bindtags(
                (
                    "transaction",
                    "transaction_amount_label",
                    f"transaction_{transaction.id}",
                )
                + amount_label.bindtags()
            )

            time_label = ttk.Label(
                self.table_frame,
                text=datetime.datetime.fromtimestamp(transaction.time).strftime(
                    sadf("%a %-d %b %Y %-I:%M:%S %p")
                ),
                style="SaintsPayStyle.L.TLabel",
                # tag="transaction",
            )
            time_label.grid(row=i, column=3, sticky="W", padx=(10, 0))
            time_label.bindtags(
                (
                    "transaction",
                    "transaction_time_label",
                    f"transaction_{transaction.id}",
                )
                + time_label.bindtags()
            )

            operator_label = ttk.Label(
                self.table_frame,
                text=transaction.operator,
                style="SaintsPayStyle.L.TLabel",
                # tag="transaction",
            )
            operator_label.grid(row=i, column=4, sticky="W", padx=(10, 0))
            operator_label.bindtags(
                (
                    "transaction",
                    "transaction_operator_label",
                    f"transaction_{transaction.id}",
                )
                + operator_label.bindtags()
            )

            separator = ttk.Separator(
                self.table_frame,
                orient=HORIZONTAL,
            )
            separator.grid(row=i + 1, column=0, columnspan=5, sticky="WE")
            separator.bindtags(
                (
                    "transaction",
                    "transaction_separator",
                    f"transaction_{transaction.id}",
                )
                + separator.bindtags()
            )
