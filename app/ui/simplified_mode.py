from tkinter import *
from tkinter import ttk
import backend.ole
import backend.transaction
from . import (
    new_transaction,
    student_search,
    on_screen_keyboard,
    transactions_list,
    export_transactions,
    alert,
)
from utils.tkinter.center import center_within_rect
from datetime import datetime
from utils.system_agnostic_datetime_format import sadf
import utils.system_sans_font


class Window(Toplevel):
    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
    ):
        Toplevel.__init__(self, master)
        self.attributes("-fullscreen", True)

        self.ole = ole

        self.session_start_time = int(datetime.now().timestamp())

        def open_menu():
            self.menu = Menu(
                self,
                self.ole,
                exit_callback=lambda: self.destroy(),
                session_start_time=self.session_start_time,
                start_hidden=True,
            )
            center_within_rect(
                self.menu,
                self.menu_popup_rect,
                resize_window_if_larger=True,
            )

        self.menu_button = ttk.Button(
            self,
            text="Menu",
            command=open_menu,
            padding=5,
            style="SaintsPayStyle.Simplified.TButton",
        )
        self.menu_button.pack(side=TOP, anchor="ne", padx=10, pady=10)

        self.update_idletasks()

        self.spacing = 10
        self.sidebar_width = 600 * utils.system_sans_font.window_size_multiplier
        self.menu_popup_height = 400 * utils.system_sans_font.window_size_multiplier

        self.screen_rect = {
            "x": 0,
            "y": 0,
            "width": self.winfo_screenwidth(),
            "height": self.winfo_screenheight(),
        }
        self.primary_rect = {
            "x": self.spacing,
            "y": self.spacing,
            "width": self.screen_rect["width"] - self.sidebar_width - self.spacing * 3,
            "height": self.screen_rect["height"] - self.spacing * 2,
        }
        self.menu_popup_rect = {
            "x": self.spacing * 2 + self.primary_rect["width"],
            "y": self.spacing * 2 + self.menu_button.winfo_height(),
            "width": self.sidebar_width,
            "height": self.menu_popup_height,
        }
        self.numpad_rect = {
            "x": self.spacing * 2 + self.primary_rect["width"],
            "y": self.spacing * 3
            + self.menu_button.winfo_height()
            + self.menu_popup_rect["height"],
            "width": self.sidebar_width,
            "height": self.screen_rect["height"]
            - self.spacing * 4
            - self.menu_popup_rect["height"]
            - self.menu_button.winfo_height(),
        }

        self.student_search_window = None
        self.new_transaction_window = None

        def select_command(student):
            self.student_search_window.withdraw()

            self.new_transaction_window = new_transaction.Window(
                master=self,
                student=student,
                ole=self.ole,
                is_simplified_mode=True,
                window_close_callback=open_student_search_window,
                confirm_transaction_rect=self.menu_popup_rect,
                start_hidden=True,
            )
            center_within_rect(
                self.new_transaction_window,
                self.primary_rect,
                resize_window_if_larger=True,
            )

            self.numpad_window = on_screen_keyboard.Window(
                self.new_transaction_window,
                event_listener=self.new_transaction_window.keypad_event_listener,
                special_keys={
                    "back\nspace": "SPECIAL_BACKSPACE",
                    "enter": "SPECIAL_ENTER",
                },
                keyboard_symbols={
                    "␋": "back\nspace",
                    "␤": "enter",
                },
                keyboard=(
                    "7†8†9†␋†" + "\n"
                    "††††††††" + "\n"
                    "4¦5¦6‡††" + "\n"
                    "¦¦¦¦‡‡††" + "\n"
                    "1†2†3¦␤¦" + "\n"
                    "††††¦¦¦¦" + "\n"
                    "0¦¦¦.†¦¦" + "\n"
                    "¦¦¦¦††¦¦"
                ),
                start_hidden=True,
            )
            center_within_rect(
                self.numpad_window,
                self.numpad_rect,
                resize_window_if_larger=False,
            )

        def open_student_search_window():
            if (
                self.new_transaction_window is not None
                and self.new_transaction_window.winfo_exists()
            ):
                self.new_transaction_window.destroy()

            if (
                self.new_transaction_window is not None
                and self.student_search_window.winfo_exists()
                and not self.student_search_window.winfo_ismapped()
            ):
                self.student_search_window.deiconify()
                self.student_search_window.focus()

                self.student_search_window.select_all_and_open_keyboard()
                return

            self.student_search_window = student_search.Window(
                self,
                self.ole,
                title="Payment Terminal",
                select_command=select_command,
                is_simplified_mode=True,
                window_close_callback=lambda: None,
                start_hidden=True,
            )
            center_within_rect(
                self.student_search_window,
                self.primary_rect,
                resize_window_if_larger=True,
            )

        open_student_search_window()


class Menu(Toplevel):
    def __init__(
        self, master, ole, exit_callback, session_start_time, start_hidden=False
    ):
        Toplevel.__init__(self, master)
        if start_hidden:
            self.attributes("-alpha", 0.0)

        self.title("Menu")
        self.geometry("400x300")
        self.attributes("-topmost", True)

        self.ole = ole

        self.view_button = ttk.Button(
            self,
            text="View Transactions",
            command=lambda: transactions_list.Window(
                self,
                self.ole,
                filter=backend.transaction.TransactionFilter(
                    from_start_of_time=session_start_time,
                ),
                is_simplified_mode=True,
            ),
            padding=10,
            style="SaintsPayStyle.Simplified.TButton",
        )
        self.view_button.pack(
            side=TOP, anchor="nw", padx=10, pady=(10, 5), expand=True, fill=BOTH
        )

        def export_transactions_command():
            transactions__ = backend.transaction.get_transactions_filtered(
                backend.transaction.TransactionFilter(
                    from_start_of_time=session_start_time,
                )
            )

            if len(transactions__) == 0:
                alert.Window(
                    self,
                    "No Transactions",
                    "There are no transactions to export.",
                    style="info",
                    buttons=["OK"],
                    topmost=True,
                )
                return

            exit_callback()

            export_transactions.Window.export_transactions(
                self.ole,
                transactions__,
                filename=f"Transactions--{datetime.now().strftime(sadf('%-d-%m-%y'))}.xlsx",
            )

        self.done_button = ttk.Button(
            self,
            text="Done & Export Transactions",
            command=export_transactions_command,
            padding=10,
            style="SaintsPayStyle.Simplified.TButton",
        )
        self.done_button.pack(
            side=TOP, anchor="nw", padx=10, pady=5, expand=True, fill=BOTH
        )

        def exit_button_pressed():
            # show alert
            def callback(button):
                if button == "Cancel":
                    return

                exit_callback()

            alert.Window(
                self,
                "Exit Simplified Mode",
                "Are you sure you want to exit Simplified Mode?",
                style="warning",
                buttons=["Cancel", "Exit Simplified Mode"],
                callback=callback,
                topmost=True,
            )

        self.exit_button = ttk.Button(
            self,
            text="Exit Simplified Mode",
            command=exit_button_pressed,
            padding=10,
            style="SaintsPayStyle.Simplified.TButton",
        )
        self.exit_button.pack(
            side=TOP, anchor="nw", padx=10, pady=5, expand=True, fill=BOTH
        )

        # close button

        def close_button_pressed():
            self.destroy()

        self.close_button = ttk.Button(
            self,
            text="Close Menu",
            command=close_button_pressed,
            padding=10,
            style="SaintsPayStyle.Simplified.TButton",
        )
        self.close_button.pack(
            side=TOP, anchor="nw", padx=10, pady=(5, 10), expand=True, fill=BOTH
        )
