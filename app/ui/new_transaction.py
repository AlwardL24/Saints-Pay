from tkinter import *
from tkinter import ttk
import ui.alert
from utils.tkinter.entry_with_placeholder import EntryWithPlaceholder
import time
from threading import Timer, Thread
import backend.ole
import backend.notes
import backend.blacklist
import backend.transaction
from PIL import ImageTk, Image
import utils.user_data_directory as udd
import os
from . import edit_notes, confirm_transaction, blacklist_reason, transactions_list
from datetime import datetime, timedelta
from utils.system_agnostic_datetime_format import sadf
from utils.tkinter.center import center, center_within_rect
import utils.system_sans_font


class Window(Toplevel):
    def __init__(
        self,
        master,
        student: backend.ole.OLE.Student,
        ole: backend.ole.OLE,
        is_simplified_mode=False,
        window_close_callback=None,
        confirm_transaction_rect=None,
        start_hidden=False,
    ):
        Toplevel.__init__(self, master)
        if start_hidden:
            self.attributes("-alpha", 0.0)

        self.title(f"New Transaction [{student.name}]")

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 775)}x{int(utils.system_sans_font.window_size_multiplier * 370)}"
            if not is_simplified_mode
            else f"{int(utils.system_sans_font.window_size_multiplier * 940)}x{int(utils.system_sans_font.window_size_multiplier * 430)}"
        )
        self.resizable(True, True)

        self.ole = ole

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        # frame.rowconfigure(0, weight=1)
        # frame.rowconfigure(2, weight=1)
        # frame.rowconfigure(5, weight=1)
        # frame.rowconfigure(7, weight=1)
        # frame.rowconfigure(11, weight=1)
        # frame.rowconfigure(13, weight=2)
        # frame.rowconfigure(14, weight=2)

        frame.rowconfigure(9, weight=1)

        frame.columnconfigure(1, weight=1)

        image = Image.open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../assets/placeholder_user_image.png",
            )
        )
        image.thumbnail((210, 270), Image.LANCZOS)

        image = ImageTk.PhotoImage(image)
        imageLabel = Label(frame, image=image, height=270, width=210, bg=self["bg"])
        imageLabel.image = image  # Prevents Garbage Collection
        imageLabel.grid(
            row=0, column=0, rowspan=9, sticky="NWSE", padx=(0, 10), pady=(0, 20)
        )

        nameLabel = ttk.Label(
            frame,
            text=f"{student.name}",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.BoldXXL.TLabel",
        )
        nameLabel.grid(row=0, column=1, sticky="NWS", pady=(0, 5))

        infoLabel = ttk.Label(
            frame,
            text=f"Year {student.year if student.year is not None else 'Unknown'} • {student.tutor if student.tutor is not None else 'Unknown'} • {student.id}",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TLabel",
        )
        infoLabel.grid(row=1, column=1, sticky="NWS")

        emailLabel = ttk.Label(
            frame,
            text=f"{student.email}",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TLabel",
        )
        emailLabel.grid(row=2, column=1, sticky="NWS", pady=(0, 5))

        notesTitleLabel = ttk.Label(
            frame,
            text=f"Notes:",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.BoldL.TLabel",
        )
        notesTitleLabel.grid(row=3, column=1, sticky="NWS")

        notesLabel = ttk.Label(
            frame,
            text=backend.notes.get_notes_for_student(student.schoolbox_id),
            style="SaintsPayStyle.Simplified.TLabel" if is_simplified_mode else None,
        )
        notesLabel.grid(row=4, column=1, sticky="NWSE", pady=(0, 5))

        notesLabel.bind(
            "<Configure>",
            lambda _: notesLabel.config(wraplength=notesLabel.winfo_width()),
        )

        totalAmountSpentHeadingLabel = ttk.Label(
            frame,
            text=f"Total Amount Spent",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.BoldL.TLabel",
        )
        totalAmountSpentHeadingLabel.grid(row=5, column=1, sticky="NWS")

        transactionsToday = backend.transaction.get_transactions_filtered(
            backend.transaction.TransactionFilter(
                student_schoolbox_id=student.schoolbox_id,
                from_start_of=datetime.now().date(),
            )
        )

        totalAmountSpentToday = sum(
            [transaction.amount for transaction in transactionsToday]
        )

        totalAmountSpentTodayLabel = ttk.Label(
            frame,
            text=f"Today: ${totalAmountSpentToday:.2f}",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TLabel",
        )
        totalAmountSpentTodayLabel.grid(row=6, column=1, sticky="NWS")

        print(
            (datetime.today() - timedelta(days=datetime.today().weekday() % 7)).date()
        )

        transactionsThisWeek = backend.transaction.get_transactions_filtered(
            backend.transaction.TransactionFilter(
                student_schoolbox_id=student.schoolbox_id,
                from_start_of=(
                    datetime.today() - timedelta(days=datetime.today().weekday() % 7)
                ).date(),
            )
        )

        totalAmountSpentThisWeek = sum(
            [transaction.amount for transaction in transactionsThisWeek]
        )

        totalAmountSpentThisWeekLabel = ttk.Label(
            frame,
            text=f"This Week: ${totalAmountSpentThisWeek:.2f}",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TLabel",
        )
        totalAmountSpentThisWeekLabel.grid(row=7, column=1, sticky="NWS", pady=(0, 10))

        actionButtonsFrame = ttk.Frame(frame)
        actionButtonsFrame.grid(row=8, column=1, sticky="NWS", pady=(0, 20))

        def toggle_blacklist():
            if backend.blacklist.is_student_blacklisted(student.schoolbox_id):
                backend.blacklist.remove_student_from_blacklist(student.schoolbox_id)
                blacklistButton.configure(text="Add to Blacklist")
            else:
                blacklist_reason.Window(self, student)
                blacklistButton.configure(text="Remove from Blacklist")

        blacklistButton = ttk.Button(
            actionButtonsFrame,
            text="Add to Blacklist",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TButton",
            command=toggle_blacklist,
        )
        blacklistButton.grid(row=0, column=0, sticky="NWSE", padx=5)

        if backend.blacklist.is_student_blacklisted(student.schoolbox_id):
            blacklistButton.configure(text="Remove from Blacklist")

            blacklist_entry = backend.blacklist.get_blacklist_entry_for_student(
                student.schoolbox_id
            )

            self.after(
                20,
                lambda: ui.alert.Window(
                    self,
                    "Blacklisted",
                    f"Caution: {student.name} is blacklisted!\n\nBlacklisted by {blacklist_entry.operator} at {datetime.fromtimestamp(blacklist_entry.time).strftime(sadf('%a %-d %b %Y %-I:%M:%S %p'))}\nReason:\n{blacklist_entry.reason}",
                    "warning",
                    topmost=is_simplified_mode,
                ),
            )

        editNotesButton = ttk.Button(
            actionButtonsFrame,
            text="Edit Notes",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TButton",
            command=lambda: edit_notes.Window(
                self,
                student,
                lambda: notesLabel.configure(
                    text=backend.notes.get_notes_for_student(student.schoolbox_id)
                ),
                is_simplified_mode=is_simplified_mode,
            ),
        )
        editNotesButton.grid(row=0, column=1, sticky="NWSE", padx=5)

        viewPastTransactionsButton = ttk.Button(
            actionButtonsFrame,
            text="View Past Transactions",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TButton",
            command=lambda: transactions_list.Window(
                self,
                ole,
                backend.transaction.TransactionFilter(
                    student_schoolbox_id=student.schoolbox_id,
                ),
                is_simplified_mode=is_simplified_mode,
            ),
        )
        viewPastTransactionsButton.grid(row=0, column=2, sticky="NWSE", padx=5)

        cost_bar_frame = ttk.Frame(frame)
        cost_bar_frame.grid(row=9, column=0, columnspan=3, sticky="WSE")

        cost_bar_frame.columnconfigure(0, weight=1)

        cost_entry = EntryWithPlaceholder(
            cost_bar_frame,
            placeholder="Transaction Amount (e.g. 5.00)",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TEntry",
            justify=LEFT,
            exportselection=0,
            font=(
                utils.system_sans_font.normal,
                int(18 * utils.system_sans_font.size_multiplier),
            )
            if is_simplified_mode
            else (
                utils.system_sans_font.normal,
                int(12 * utils.system_sans_font.size_multiplier),
            ),
            # keytyped_callback=self.search_entry_keytyped_callback,
        )
        cost_entry.grid(row=0, column=0, sticky="NWSE", padx=(0, 5))

        cost_entry.focus()

        cost_entry.bind("<Return>", lambda _: done_button_pressed())

        cancel_button = ttk.Button(
            cost_bar_frame,
            text="Cancel",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TButton",
            command=lambda: window_close_callback()
            if window_close_callback is not None
            else self.destroy(),
        )
        cancel_button.grid(row=0, column=1, sticky="NWSE", padx=5)

        def done_button_pressed():
            try:
                text = cost_entry.get().strip()
                if text.startswith("$"):
                    text = text[1:]

                if text.endswith("."):
                    text = text[:-1]

                if text.startswith("."):
                    text = f"0{text}"

                if len(text.split(".")) == 2:
                    decimal = text.split(".")[1]
                    if len(decimal) > 2:
                        decimal_to_round = float(f"{decimal[:2]}.{decimal[2:]}")
                        decimal = round(decimal_to_round)
                        text = f"{text.split('.')[0]}.{str(decimal).zfill(2)}"

                cost = float(text)

                if cost <= 0:
                    raise ValueError()
            except ValueError:
                ui.alert.Window(
                    self,
                    "Invalid Amount",
                    'The transaction amount you entered is invalid. Please enter a valid amount, of the format "5.50".',
                    "error",
                    topmost=is_simplified_mode,
                )
                return

            def canceled_callback():
                 self.confirm_transaction_callback = None

            confirm_transaction_window = confirm_transaction.Window(
                self,
                student,
                cost,
                lambda: window_close_callback()
                if window_close_callback is not None
                else self.destroy(),
                canceled_callback=canceled_callback,
                is_simplified_mode=is_simplified_mode,
            )
            if confirm_transaction_rect is not None:
                center_within_rect(
                    confirm_transaction_window, confirm_transaction_rect, True
                )
            else:
                center(confirm_transaction_window)

            self.confirm_transaction_callback = confirm_transaction_window.confirm

        done_button = ttk.Button(
            cost_bar_frame,
            text="Done",
            style=f"SaintsPayStyle{ '.Simplified' if is_simplified_mode else '' }.L.TButton",
            command=done_button_pressed,
        )
        done_button.grid(row=0, column=2, sticky="NWSE", padx=(5, 0))

        def get_extra_student_info(student, imageLabel, infoLabel, emailLabel):
            cached_image = self.ole.get_student_image_from_cache(student)

            if cached_image is not None:
                image = cached_image
                image.thumbnail((210, 270), Image.LANCZOS)

                image = ImageTk.PhotoImage(image)
                imageLabel.configure(image=image)
                imageLabel.image = image  # Prevents Garbage Collection
                print(f"FOUND CACHED PHOTO FOR STUDENT {student.schoolbox_id}")

            if student.email is None:
                print(f"LOADING EXTRA DETAILS FOR STUDENT {student.schoolbox_id}")

                student = self.ole.student(student)

                infoLabel.configure(
                    text=f"Year {student.year if student.year is not None else 'Unknown'} • {student.tutor if student.tutor is not None else 'Unknown'} • {student.id}"
                )

                emailLabel.configure(
                    text=f"{student.email}",
                )

            if cached_image is None:
                print(f"DOWNLOADING PHOTO FOR STUDENT {student.schoolbox_id}")

                image = self.ole.get_student_image(student, try_cache=False)
                image.thumbnail((210, 270), Image.LANCZOS)

                image = ImageTk.PhotoImage(image)
                imageLabel.configure(image=image)
                imageLabel.image = image  # Prevents Garbage Collection

        thread = Thread(
            target=get_extra_student_info,
            args=(student, imageLabel, infoLabel, emailLabel),
        )
        thread.start()

        if window_close_callback is not None:
            self.protocol("WM_DELETE_WINDOW", lambda: window_close_callback())

        if is_simplified_mode:

            def listener(event):
                if event["type"] == "SPECIAL":
                    if event["key"] == "BACKSPACE":
                        if cost_entry.showing_placeholder:
                            return
                        cost_entry.delete(cost_entry.index(INSERT) - 1)
                    elif event["key"] == "ENTER":
                        try:
                            if self.confirm_transaction_callback is not None:
                                self.confirm_transaction_callback()
                                return
                        except:
                            pass

                        done_button_pressed()
                else:
                    cost_entry.insert(cost_entry.index(INSERT), event["key"])

                cost_entry.selection_range(
                    cost_entry.index(INSERT) - 1, cost_entry.index(INSERT)
                )

                cost_entry.placeholder_check()

            self.keypad_event_listener = listener


# from ttkthemes import ThemedTk

# root = ThemedTk(theme="arc", toplevel=True)
# root.withdraw()

# window = Window(root, backend.ole.OLE.Student(id="123", name="John Smith"), None)

# root.mainloop()
