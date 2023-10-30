from tkinter import *
from tkinter import ttk
from . import (
    transactions_list,
    payment_terminal,
    export_transactions,
    alert,
    simplified_mode,
)
import backend.ole
from utils.tkinter.center import center
import utils.system_sans_font


class Window(Toplevel):
    open_payment_terminal_callback = None

    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
        log_out_callback: callable,
        quit_callback=None,
    ):
        Toplevel.__init__(self, master)

        self.title("Saints Pay")

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 724)}x{int(utils.system_sans_font.window_size_multiplier * 433)}"
        )
        self.resizable(True, True)

        self.quit_callback = quit_callback

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=6)
        frame.rowconfigure(2, weight=4)
        frame.rowconfigure(4, minsize=15)
        frame.rowconfigure(7, minsize=15)
        frame.rowconfigure(9, minsize=15)
        frame.rowconfigure(11, weight=4)

        title = ttk.Label(
            frame,
            text="Saints Pay",
            style="SaintsPayStyle.BoldXXL.TLabel"
            # font=(utils.system_sans_font.bold, 24),
        )
        title.grid(row=0, column=0, sticky="NW")

        version = ttk.Label(
            frame,
            text="Version 1.2.5",
            style="SaintsPayStyle.L.TLabel"
            # font=(utils.system_sans_font.normal, 12),
        )
        version.grid(row=1, column=0, sticky="NW")

        ole_login_status = ttk.Label(
            frame,
            text=f"Logged into the OLE as {ole.username} ({ole.role})",
            # font=(utils.system_sans_font.normal, 12),
        )
        ole_login_status.grid(row=0, column=1, sticky="NE", pady=(0, 5))

        ole_logout_button = ttk.Button(
            frame,
            text="Log out",
            # style="SaintsPayStyle.Normal.12.TButton",
            command=log_out_callback,
        )
        ole_logout_button.grid(row=1, column=1, sticky="NE")

        def start_simplified_mode():
            def callback(button):
                if button == "Cancel":
                    return

                simplified_mode.Window(self.master, ole)

            alert.Window(
                self,
                "Simplified Mode",
                "Simplified Mode simplifies the Saints Pay Workflow as much as possible. Simplified Mode can be used with a touchscreen or mouse. To exit Simplified Mode, click the 'Menu' button in the top right corner of the window.",
                style="info",
                buttons=["Cancel", "Start Simplified Mode"],
                callback=callback,
            )

        simplified_mode_button = ttk.Button(
            frame,
            text="Start Simplified Mode",
            # font=(utils.system_sans_font.normal, 12),
            # padx=10,
            # pady=5,
            # relief=RAISED,
            command=start_simplified_mode,
        )
        simplified_mode_button.grid(row=12, column=1, sticky="SE")

        open_payment_terminal_button = ttk.Button(
            frame,
            text="Open payment terminal",
            # font=(utils.system_sans_font.normal, 12),
            # padx=10,
            # pady=5,
            # relief=RAISED,
            command=lambda: payment_terminal.Window(self.master, ole=ole),
        )
        open_payment_terminal_button.grid(row=3, column=0, sticky="NSWE")

        view_transactions_button = ttk.Button(
            frame,
            text="View & edit transactions",
            # font=(utils.system_sans_font.normal, 12),
            # padx=10,
            # pady=5,
            # relief=RAISED,
            command=lambda: transactions_list.Window(self.master, ole),
        )
        view_transactions_button.grid(row=5, column=0, sticky="NSWE", pady=(0, 2))

        export_transactions_button = ttk.Button(
            frame,
            text="Export transactions to Excel",
            # font=(utils.system_sans_font.normal, 12),
            # padx=10,
            # pady=5,
            # relief=RAISED,
            command=lambda: export_transactions.Window(self.master, ole),
        )
        export_transactions_button.grid(row=6, column=0, sticky="NSWE")

        # delete_transactions_button = ttk.Button(
        #     frame,
        #     text="Delete transactions",
        #     # font=(utils.system_sans_font.normal, 12),
        #     # padx=10,
        #     # pady=5,
        #     # relief=RAISED,
        # )
        # delete_transactions_button.grid(row=8, column=0, sticky="NSWE")

        clear_student_cache_button = ttk.Button(
            frame,
            text="Clear student cache",
            # font=(utils.system_sans_font.normal, 12),
            # padx=10,
            # pady=5,
            # relief=RAISED,
            command=lambda: ole.clear_student_cache(),
        )
        clear_student_cache_button.grid(row=10, column=0, sticky="NSWE")

        self.protocol("WM_DELETE_WINDOW", self.on_destroy)

        center(self)

    def on_destroy(self):
        if self.quit_callback is not None:
            button = ""

            def alert_callback(_button):
                nonlocal button
                button = _button

            alert.Window(
                self,
                "Quit Saints Pay",
                "Are you sure you want to quit Saints Pay? This will close all other windows",
                style="warning",
                buttons=["Cancel", "Quit"],
                callback=alert_callback,
            ).wait_window()

            if button == "Quit":
                self.quit_callback()
