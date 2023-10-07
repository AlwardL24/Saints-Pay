from tkinter import *
from tkinter import ttk
from . import transactions_list, payment_terminal, export_transactions
import backend.ole


class Window(Toplevel):
    open_payment_terminal_callback = None

    def __init__(self, master, ole: backend.ole.OLE, log_out_callback: callable):
        Toplevel.__init__(self, master)

        self.title("Saints Pay")

        self.geometry("724x433")
        self.resizable(True, True)

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
            text="Version 1.0",
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

        # check_for_updates_button = ttk.Button(
        #     frame,
        #     text="Check for updates",
        #     # font=(utils.system_sans_font.normal, 12),
        #     # padx=10,
        #     # pady=5,
        #     # relief=RAISED,
        # )
        # check_for_updates_button.grid(row=12, column=1, sticky="SE")

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
