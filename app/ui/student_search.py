from tkinter import *
from tkinter import ttk
from typing import Callable
from utils.tkinter.entry_with_placeholder import EntryWithPlaceholder
from utils.tkinter.smooth_scrolled_text import SmoothScrolledText
import utils.system_sans_font
import time
from threading import Timer, Thread
import backend.ole
from PIL import ImageTk, Image
import os
from . import on_screen_keyboard


class Window(Toplevel):
    search_entry_last_keytyped_time = None
    search_entry_keytyped_timer = None

    def __init__(
        self,
        master,
        ole: backend.ole.OLE,
        title: str,
        select_command: Callable[[backend.ole.OLE.Student], None],
        is_simplified_mode: bool = False,
        window_close_callback: callable = None,
    ):
        Toplevel.__init__(self, master)
        self.title(title)

        if is_simplified_mode:
            self.attributes("-topmost", True)

        self.geometry(
            f"{int(utils.system_sans_font.window_size_multiplier * 724)}x{int(utils.system_sans_font.window_size_multiplier * 770)}"
        )
        self.resizable(True, True)

        self.ole = ole
        self.select_command = select_command

        self.is_simplified_mode = is_simplified_mode

        self.on_screen_keyboard = None
        self.on_screen_keyboard_was_showing = False

        frame = ttk.Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        self.search_entry = EntryWithPlaceholder(
            frame,
            placeholder="Search for a student or scan their ID card...",
            exportselection=0,
            keytyped_callback=self.search_entry_keytyped_callback,
            font=(
                utils.system_sans_font.normal,
                int(18 * utils.system_sans_font.size_multiplier),
            )
            if is_simplified_mode
            else (
                utils.system_sans_font.normal,
                int(12 * utils.system_sans_font.size_multiplier),
            ),
        )
        self.search_entry.grid(row=0, column=0, sticky="NWSE")

        self.search_entry.focus_set()

        self.search_entry.bind(
            "<Return>",
            lambda _: self.search_or_scan_for(self.search_entry.get(), False),
        )

        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=1, sticky="NWSE", padx=(5, 0))

        if is_simplified_mode:
            show_keyboard_button = ttk.Button(
                buttons_frame,
                text="Show Keyboard",
                command=self.show_keyboard_button_pressed,
                style="SaintsPayStyle.Simplified.TButton",
            )
            show_keyboard_button.grid(row=0, column=0, sticky="NWSE", padx=(0, 5))

        search_button = ttk.Button(
            buttons_frame,
            text="Search",
            command=lambda: self.search_or_scan_for(self.search_entry.get(), False),
            style="SaintsPayStyle.Simplified.TButton" if is_simplified_mode else None,
        )
        search_button.grid(
            row=0, column=0 if not is_simplified_mode else 1, sticky="NWSE"
        )

        self.results_label = ttk.Label(
            frame,
            text="No results",
            justify=LEFT,
            style="SaintsPayStyle.Simplified.TLabel" if is_simplified_mode else None,
        )
        self.results_label.grid(row=1, column=0, sticky="NWS", columnspan=2, pady=5)

        self.results_box = SmoothScrolledText(
            frame,
            state="disabled",
            bg=self["bg"],
            highlightthickness=1,
            highlightbackground="#cdd6e8",
            borderwidth=0,
            wrap=WORD,
            cursor="arrow",
        )
        self.results_box.grid(row=2, column=0, sticky="NWSE", columnspan=2)

        if window_close_callback is not None:
            self.protocol("WM_DELETE_WINDOW", lambda: window_close_callback())

    def select_command_constructor(self, student):
        return lambda: self.select_command(student)

    def search_or_scan_for(self, value, is_scan):
        if (
            self.on_screen_keyboard is not None
            and self.on_screen_keyboard.winfo_exists()
        ):
            self.on_screen_keyboard.destroy()
            self.on_screen_keyboard = None

        self.results_label.configure(text=f'Searching for "{value}"...')

        def make_request():
            students = self.ole.search_students(value)

            if is_scan and len(students) > 0:
                self.results_label.configure(
                    text=f'Scanned "{value}" - {students[0].name}'
                )
                self.select_command_constructor(students[0])()
                return

            if not is_scan and len(students) == 1:
                self.results_label.configure(
                    text=f'Searched for "{value}" - {students[0].name}'
                )
                self.select_command_constructor(students[0])()
                return

            self.results_label.configure(
                text=f'{len(students)} result{"s" if len(students) != 1 else ""} for "{value}"'
            )

            self.results_box.configure(state="normal")
            self.results_box.delete("1.0", "end")

            for student in students:
                resultFrame = ttk.Frame(self.results_box)

                resultFrame.columnconfigure(1, weight=1)

                image = Image.open(
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        "../assets/placeholder_user_image.png",
                    )
                )
                image.thumbnail((70, 70), Image.LANCZOS)

                image = ImageTk.PhotoImage(image)
                imageLabel = Label(
                    resultFrame, image=image, height=70, width=70, bg=self["bg"]
                )
                imageLabel.image = image  # Prevents Garbage Collection
                imageLabel.grid(
                    row=0, column=0, rowspan=3, sticky="NWSE", padx=5, pady=5
                )

                nameLabel = ttk.Label(
                    resultFrame,
                    text=f"{student.name}",
                    style=f"SaintsPayStyle{ '.Simplified' if self.is_simplified_mode else '' }.BoldL.TLabel",
                )
                nameLabel.grid(row=0, column=1, sticky="NWS", pady=(5, 0))

                infoLabel = ttk.Label(
                    resultFrame,
                    text=f"Loading...",
                    style="SaintsPayStyle.Simplified.TLabel"
                    if self.is_simplified_mode
                    else None,
                )
                infoLabel.grid(row=1, column=1, sticky="NWS")

                selectButton = ttk.Button(
                    resultFrame,
                    text="Select",
                    command=self.select_command_constructor(student),
                    style="SaintsPayStyle.Simplified.TButton"
                    if self.is_simplified_mode
                    else None,
                )
                selectButton.grid(row=2, column=1, sticky="SW", pady=(0, 5))

                self.results_box.window_create(END, window=resultFrame)
                self.results_box.insert(END, "\n")

                def get_extra_student_info(student, imageLabel, infoLabel):
                    print(student.schoolbox_id)

                    cached_image = self.ole.get_student_image_from_cache(student)

                    if cached_image is not None:
                        image = cached_image
                        image.thumbnail((70, 70), Image.LANCZOS)

                        image = ImageTk.PhotoImage(image)
                        imageLabel.configure(image=image)
                        imageLabel.image = image  # Prevents Garbage Collection
                        print(f"FOUND CACHED PHOTO FOR STUDENT {student.schoolbox_id}")

                    print(f"LOADING EXTRA DETAILS FOR STUDENT {student.schoolbox_id}")

                    student = self.ole.student(student)

                    infoLabel.configure(
                        text=f"Year {student.year if student.year is not None else 'Unknown'} • {student.tutor if student.tutor is not None else 'Unknown'} • {student.username}"
                    )

                    if cached_image is None:
                        print(f"DOWNLOADING PHOTO FOR STUDENT {student.schoolbox_id}")

                        image = self.ole.get_student_image(student, try_cache=False)
                        image.thumbnail((70, 70), Image.LANCZOS)

                        image = ImageTk.PhotoImage(image)
                        imageLabel.configure(image=image)
                        imageLabel.image = image  # Prevents Garbage Collection

                thread = Thread(
                    target=get_extra_student_info, args=(student, imageLabel, infoLabel)
                )
                thread.start()

            self.results_box.configure(state="disabled")

        thread = Thread(target=make_request)
        thread.start()

    def search_entry_keytyped_callback(self, value):
        if len(value) == 1 and self.search_entry_last_keytyped_time is None:
            self.search_entry_last_keytyped_time = time.time()

        if not self.search_entry_last_keytyped_time is None:
            if not self.search_entry_keytyped_timer is None:
                self.search_entry_keytyped_timer.cancel()

            def callback():
                self.search_entry_last_keytyped_time = None
                self.search_entry_keytyped_timer = None

                if len(value) <= 2:
                    return

                if len("".join(c for c in value if c.isdigit())) <= 2:
                    return

                self.search_entry.clear()

                self.search_or_scan_for("".join(c for c in value if c.isdigit()), True)

            self.search_entry_keytyped_timer = Timer(
                0.07,
                lambda: callback(),
            )

            self.search_entry_keytyped_timer.start()

    def on_screen_keyboard_event_listener(self, event):
        if event["type"] == "SPECIAL":
            if event["key"] == "BACKSPACE":
                if self.search_entry.showing_placeholder:
                    return

                if (
                    self.search_entry.select_present()
                    and self.search_entry.index("sel.first") == 0
                    and self.search_entry.index("sel.last")
                    == len(self.search_entry.get())
                    and self.search_entry.index("sel.last") != 1
                ):
                    self.search_entry.clear()
                    return

                self.search_entry.delete(self.search_entry.index(INSERT) - 1)
            elif event["key"] == "ENTER":
                self.search_or_scan_for(self.search_entry.get(), False)
            elif event["key"] == "SPACE":
                if (
                    self.search_entry.select_present()
                    and self.search_entry.index("sel.first") == 0
                    and self.search_entry.index("sel.last")
                    == len(self.search_entry.get())
                    and self.search_entry.index("sel.last") != 1
                ):
                    self.search_entry.clear()

                self.search_entry.insert(self.search_entry.index(INSERT), " ")
            elif event["key"] == "ARROW_LEFT":
                self.search_entry.icursor(self.search_entry.index(INSERT) - 1)
            elif event["key"] == "ARROW_RIGHT":
                self.search_entry.icursor(self.search_entry.index(INSERT) + 1)
        else:
            if (
                self.search_entry.select_present()
                and self.search_entry.index("sel.first") == 0
                and self.search_entry.index("sel.last") == len(self.search_entry.get())
                and self.search_entry.index("sel.last") != 1
            ):
                self.search_entry.clear()

            self.search_entry.insert(self.search_entry.index(INSERT), event["key"])

        self.search_entry.selection_range(
            self.search_entry.index(INSERT) - 1, self.search_entry.index(INSERT)
        )

        self.search_entry.placeholder_check()

    def show_keyboard_button_pressed(self):
        def closed():
            self.on_screen_keyboard_was_showing = False

        self.on_screen_keyboard_was_showing = True
        self.on_screen_keyboard = on_screen_keyboard.Window(
            self,
            event_listener=self.on_screen_keyboard_event_listener,
            window_close_callback=closed,
        )

    def select_all_and_open_keyboard(self):
        self.search_entry.focus()

        self.search_entry.selection_range(0, END)

        if self.on_screen_keyboard_was_showing:
            self.show_keyboard_button_pressed()
