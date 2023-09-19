from tkinter import *


class Window(Toplevel):
    open_payment_terminal_callback = None

    def __init__(self, master, open_payment_terminal_callback):
        Toplevel.__init__(self, master)
        self.title("Saints Pay")

        self.geometry("724x433")
        self.resizable(True, True)

        self.open_payment_terminal_callback = open_payment_terminal_callback

        frame = Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=6)
        frame.rowconfigure(2, weight=4)
        frame.rowconfigure(4, weight=1)
        frame.rowconfigure(7, weight=1)
        frame.rowconfigure(9, weight=1)
        frame.rowconfigure(11, weight=4)

        title = Label(
            frame,
            text="Saints Pay",
            font=("Helvetica Bold", 24),
        )
        title.grid(row=0, column=0, sticky="NW")

        version = Label(
            frame,
            text="Version 1.0",
            font=("Helvetica", 12),
        )
        version.grid(row=1, column=0, sticky="NW")

        ole_login_status = Label(
            frame,
            text="Logged into the OLE as Lucas Alward (student)",
            font=("Helvetica", 12),
        )
        ole_login_status.grid(row=0, column=1, sticky="NE")

        ole_logout_button = Button(
            frame,
            text="Log out",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
        )
        ole_logout_button.grid(row=1, column=1, sticky="NE")

        check_for_updates_button = Button(
            frame,
            text="Check for updates",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
        )
        check_for_updates_button.grid(row=12, column=1, sticky="SE")

        open_payment_terminal_button = Button(
            frame,
            text="Open payment terminal",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
            command=self.open_payment_terminal_callback,
        )
        open_payment_terminal_button.grid(row=3, column=0, sticky="NSWE")

        view_transactions_button = Button(
            frame,
            text="View transactions",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
        )
        view_transactions_button.grid(row=5, column=0, sticky="NSWE")

        export_transactions_button = Button(
            frame,
            text="Export transactions",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
        )
        export_transactions_button.grid(row=6, column=0, sticky="NSWE")

        delete_transactions_button = Button(
            frame,
            text="Delete transactions",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
        )
        delete_transactions_button.grid(row=8, column=0, sticky="NSWE")

        clear_student_cache_button = Button(
            frame,
            text="Clear student cache",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
        )
        clear_student_cache_button.grid(row=10, column=0, sticky="NSWE")
