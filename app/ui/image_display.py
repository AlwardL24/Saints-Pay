from tkinter import *
from tkinter import ttk

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

        image = PhotoImage(file=f"images/user_{user_id}.jpg")
        imageLabel = Label(frame, image=image)
        imageLabel.image = image
        imageLabel.pack(pady=20)

        yesButton = Button(frame, text="Yes", command=lambda: yes())
        yesButton.pack(side=LEFT, padx=30)

        noButton = Button(frame, text="No", command=lambda: no())
        noButton.pack(side=RIGHT, padx=30)

        def no():
            print("No")
            self.destroy()
            return
        
        def yes():
            print("Yes")
            self.destroy()
            return