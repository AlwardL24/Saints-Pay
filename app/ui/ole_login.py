from tkinter import *
from tkinter import ttk


class Window(Toplevel):
    callback = None

    def __init__(self, master, callback):
        Toplevel.__init__(self, master)

        self.title("Login to the OLE")

        self.callback = callback

        self.geometry("350x450")
        self.resizable(False, False)

        def focus():
            self.lift()
            self.focus_force()

        self.after(10, lambda: focus())

        frame = ttk.Frame(self)
        frame.pack(fill=X, padx=20, pady=20)

        title = ttk.Label(
            frame,
            text="Login to the OLE",
            style="SaintsPayStyle.BoldXXL.TLabel",
        )
        title.pack(pady=10)

        subtitle = ttk.Label(
            frame,
            text="Required to access student information.\n A staff account is required to show\n student photos and tutor groups.",
        )
        subtitle.pack(fill=X)

        separator = ttk.Separator(frame, orient="horizontal")
        separator.pack(fill=X, pady=20)

        oleUsername = StringVar()
        olePassword = StringVar()

        oleUsernameLabel = ttk.Label(frame, text="Username:")
        oleUsernameLabel.pack()
        oleUsernameEntry = ttk.Entry(frame, textvariable=oleUsername)
        oleUsernameEntry.pack(fill=X, pady=(0, 10))

        olePasswordLabel = ttk.Label(frame, text="Password:")
        olePasswordLabel.pack()
        olePasswordEntry = ttk.Entry(frame, show="•", textvariable=olePassword)
        olePasswordEntry.pack(fill=X)

        def clicked():
            self.after(10, super(Window, self).destroy)

            callback(oleUsername.get(), olePassword.get())

        oleLoginButton = ttk.Button(
            frame,
            text="Login",
            command=clicked,
        )
        oleLoginButton.pack(fill=X, pady=20)

    def destroy(self) -> None:
        self.callback(None, None)

        return super().destroy()
