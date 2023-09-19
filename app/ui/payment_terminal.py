from tkinter import *
from utils.tkinter.entry_with_placeholder import EntryWithPlaceholder
from utils.tkinter.smooth_scrolled_text import SmoothScrolledText
import time
from threading import Timer, Thread
import backend.ole
from PIL import ImageTk, Image
import utils.user_data_directory as udd
import os


class Window(Toplevel):
    search_entry_last_keytyped_time = None
    search_entry_keytyped_timer = None

    def __init__(self, master, ole: backend.ole.OLE):
        Toplevel.__init__(self, master)
        self.title("Payment Terminal - Saints Pay")

        self.geometry("724x770")
        self.resizable(True, True)

        self.ole = ole

        frame = Frame(self)
        frame.pack(padx=30, pady=20, expand=True, fill=BOTH)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        search_entry = EntryWithPlaceholder(
            frame,
            placeholder="Search for a student or scan their ID card...",
            font=("Helvetica", 12),
            justify=LEFT,
            relief=SUNKEN,
            exportselection=0,
            keytyped_callback=self.search_entry_keytyped_callback,
        )
        search_entry.grid(row=0, column=0, sticky="NWSE")

        search_entry.focus()

        search_entry.bind(
            "<Return>", lambda _: self.search_or_scan_for(search_entry.get(), False)
        )

        search_button = Button(
            frame,
            text="Search",
            font=("Helvetica", 12),
            padx=10,
            pady=5,
            relief=RAISED,
            command=lambda: self.search_or_scan_for(search_entry.get(), False),
        )
        search_button.grid(row=0, column=1, sticky="NWSE")

        self.results_label = Label(
            frame,
            text="No results",
            font=("Helvetica", 12),
            pady=10,
            justify=LEFT,
        )
        self.results_label.grid(row=1, column=0, sticky="NWS", columnspan=2)

        self.results_box = SmoothScrolledText(
            frame,
            state="disabled",
        )
        self.results_box.grid(row=2, column=0, sticky="NWSE", columnspan=2)

    def search_or_scan_for(self, value, is_scan):
        self.results_label.configure(text=f'Searching for "{value}"...')

        def make_request():
            students = self.ole.search_students(value)

            self.results_label.configure(
                text=f'{len(students)} result{"s" if len(students) != 1 else ""} for "{value}"'
            )

            self.results_box.configure(state="normal")
            self.results_box.delete("1.0", "end")

            for student in students:
                resultFrame = Frame(self.results_box)

                resultFrame.columnconfigure(1, weight=1)

                image = Image.open(f"app/assets/placeholder_user_image.png")
                image.thumbnail((70, 70), Image.ANTIALIAS)

                image = ImageTk.PhotoImage(image)
                imageLabel = Label(resultFrame, image=image, height=70, width=70)
                imageLabel.image = image  # Prevents Garbage Collection
                imageLabel.grid(row=0, column=0, rowspan=3, sticky="NWSE")

                nameLabel = Label(
                    resultFrame,
                    text=f"{student.name}",
                    font=("Helvetica", 12),
                )
                nameLabel.grid(row=0, column=1, sticky="NWS")

                infoLabel = Label(
                    resultFrame,
                    text=f"Loading...",
                    font=("Helvetica", 12),
                )
                infoLabel.grid(row=1, column=1, sticky="NWS")

                selectButton = Button(
                    resultFrame,
                    text="Select",
                    font=("Helvetica", 12),
                    padx=10,
                    pady=5,
                    relief=RAISED,
                    command=lambda: print("MAYBE DO SOMETHING"),
                )
                selectButton.grid(row=2, column=1, sticky="SW")

                self.results_box.window_create(END, window=resultFrame)
                self.results_box.insert(END, "\n")

                def get_extra_student_info(student, imageLabel, infoLabel):
                    print(student.schoolbox_id)

                    image_cache_directory = udd.get_user_data_dir(
                        ["SaintsPay", "student-data-cache", "images"]
                    )

                    if not os.path.exists(image_cache_directory):
                        os.makedirs(image_cache_directory)

                    image_filename = f"{student.schoolbox_id}.png"

                    image_path = os.path.join(image_cache_directory, image_filename)

                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        image.thumbnail((70, 70), Image.ANTIALIAS)

                        image = ImageTk.PhotoImage(image)
                        imageLabel.configure(image=image)
                        imageLabel.image = image  # Prevents Garbage Collection
                        print(f"FOUND CACHED PHOTO FOR STUDENT {student.schoolbox_id}")

                    print(f"LOADING EXTRA DETAILS FOR STUDENT {student.schoolbox_id}")

                    student = self.ole.student(student)

                    infoLabel.configure(
                        text=f"Year {student.year if student.year is not None else 'Unknown'} • {student.tutor if student.tutor is not None else 'Unknown'} • {student.username}"
                    )

                    if not os.path.exists(image_path):
                        print(f"DOWNLOADING PHOTO FOR STUDENT {student.schoolbox_id}")
                        image_data = self.ole.get_student_image(student)
                        with open(image_path, "wb") as handler:
                            handler.write(image_data)

                        image = Image.open(image_path)
                        image.thumbnail((70, 70), Image.ANTIALIAS)

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

                self.search_or_scan_for(value, True)

            self.search_entry_keytyped_timer = Timer(
                0.07,
                lambda: callback(),
            )

            self.search_entry_keytyped_timer.start()
