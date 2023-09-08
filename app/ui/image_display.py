from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image

user_id = ""
class Window(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.title("Image Display")

        self.geometry("400x400")
        self.resizable(False, False)

        frame = Frame(self)
        frame.pack(padx=20, pady=20)

        title = Label(
            frame,
            text="Is this the student?",
            font=("Helvetica Bold", 24),
        )
        title.pack()

        image = Image.open(f"images/user_{user_id}.jpg")
        image = ImageTk.PhotoImage(image)
        imageLabel = Label(frame, image=image)
        imageLabel.image = image
        imageLabel.pack(pady=20)