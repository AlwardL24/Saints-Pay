from tkinter import *
from utils.tkinter.entry_with_placeholder import EntryWithPlaceholder
import time
from threading import Timer, Thread
import backend.ole
from PIL import ImageTk, Image
import utils.user_data_directory as udd
import os
import utils.system_sans_font


class Window(Toplevel):
    def __init__(self, master, student: backend.ole.OLE.Student, ole: backend.ole.OLE):
        Toplevel.__init__(self, master)
        self.title(f"New Transaction [{student.name}] - Saints Pay")

        self.geometry("724x400")
        self.resizable(True, True)

        self.ole = ole

        frame = Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(5, weight=1)
        frame.rowconfigure(7, weight=1)
        frame.rowconfigure(11, weight=1)
        frame.rowconfigure(13, weight=2)
        frame.rowconfigure(14, weight=2)

        frame.columnconfigure(1, minsize=20)

        image = Image.open(f"app/assets/placeholder_user_image.png")
        image.thumbnail((210, 270), Image.LANCZOS)

        image = ImageTk.PhotoImage(image)
        imageLabel = Label(frame, image=image, height=270, width=210)
        imageLabel.image = image  # Prevents Garbage Collection
        imageLabel.grid(row=0, column=0, rowspan=13, sticky="NWSE")

        nameLabel = Label(
            frame,
            text=f"{student.name}",
            font=(utils.system_sans_font.bold, 28),
        )
        nameLabel.grid(row=1, column=1, sticky="NWS")

        infoLabel = Label(
            frame,
            text=f"Year {student.year if student.year is not None else 'Unknown'} • {student.tutor if student.tutor is not None else 'Unknown'} • {student.id}",
            font=(utils.system_sans_font.normal, 14),
        )
        infoLabel.grid(row=3, column=1, sticky="NWS")

        emailLabel = Label(
            frame,
            text=f"{student.email}",
            font=(utils.system_sans_font.normal, 14),
        )
        emailLabel.grid(row=4, column=1, sticky="NWS")

        notesLabel = Label(
            frame,
            text=f"Notes: PLACEHOLDER",
            font=(utils.system_sans_font.normal, 14),
        )
        notesLabel.grid(row=6, column=1, sticky="NWS")

        totalAmountSpentHeadingLabel = Label(
            frame,
            text=f"Total Amount Spent",
            font=(utils.system_sans_font.bold, 14),
        )
        totalAmountSpentHeadingLabel.grid(row=8, column=1, sticky="NWS")

        totalAmountSpentTodayLabel = Label(
            frame,
            text=f"Today: PLACEHOLDER",
            font=(utils.system_sans_font.normal, 14),
        )
        totalAmountSpentTodayLabel.grid(row=9, column=1, sticky="NWS")

        totalAmountSpentThisWeekLabel = Label(
            frame,
            text=f"This Week: PLACEHOLDER",
            font=(utils.system_sans_font.normal, 14),
        )
        totalAmountSpentThisWeekLabel.grid(row=10, column=1, sticky="NWS")

        actionButtonsFrame = Frame(frame)
        actionButtonsFrame.grid(row=12, column=1, sticky="NWS")

        blacklistButton = Button(
            actionButtonsFrame,
            text="Add to Blacklist",
            font=(utils.system_sans_font.normal, 14),
            padx=10,
            pady=5,
            relief=RAISED,
            command=lambda: print("MAYBE DO SOMETHING"),
        )
        blacklistButton.grid(row=0, column=0, sticky="NWSE", padx=5)

        editNotesButton = Button(
            actionButtonsFrame,
            text="Edit Notes",
            font=(utils.system_sans_font.normal, 14),
            padx=10,
            pady=5,
            relief=RAISED,
            command=lambda: print("MAYBE DO SOMETHING"),
        )
        editNotesButton.grid(row=0, column=1, sticky="NWSE", padx=5)

        viewPastTransactionsButton = Button(
            actionButtonsFrame,
            text="View Past Transactions",
            font=(utils.system_sans_font.normal, 14),
            padx=10,
            pady=5,
            relief=RAISED,
            command=lambda: print("MAYBE DO SOMETHING"),
        )
        viewPastTransactionsButton.grid(row=0, column=2, sticky="NWSE", padx=5)

        cost_bar_frame = Frame(frame)
        cost_bar_frame.grid(row=15, column=0, columnspan=3, sticky="NWSE")

        cost_bar_frame.columnconfigure(0, weight=1)

        cost_entry = EntryWithPlaceholder(
            cost_bar_frame,
            placeholder="Transaction Amount (e.g. 5.00)",
            font=(utils.system_sans_font.normal, 14),
            justify=LEFT,
            relief=SUNKEN,
            exportselection=0,
            # keytyped_callback=self.search_entry_keytyped_callback,
        )
        cost_entry.grid(row=0, column=0, sticky="NWSE", padx=(0, 5))

        cost_entry.focus()

        # cost_entry.bind(
        #     "<Return>", lambda _: self.search_or_scan_for(search_entry.get(), False)
        # )

        cancel_button = Button(
            cost_bar_frame,
            text="Cancel",
            font=(utils.system_sans_font.normal, 14),
            padx=10,
            pady=5,
            relief=RAISED,
            command=lambda: self.destroy(),
        )
        cancel_button.grid(row=0, column=1, sticky="NWSE", padx=5)

        done_button = Button(
            cost_bar_frame,
            text="Done",
            font=(utils.system_sans_font.normal, 14),
            padx=10,
            pady=5,
            relief=RAISED,
            highlightbackground="orange",
            command=lambda: print("MAYBE DO SOMETHING"),
        )
        done_button.grid(row=0, column=2, sticky="NWSE", padx=(5, 0))
