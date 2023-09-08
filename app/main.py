from tkinter import *
from tkinter import messagebox
import utils.user_data_directory as udd
import keyring
import urllib.parse
import ui.startup
import ui.ole_login
import ui.scanner_setup
import time
from utils.dispatch_group import DispatchGroup
from backend.ole import OLE


root = Tk()
root.withdraw()


ole = None


def startup():
    startup_window = ui.startup.Window(root)

    # check for OLE login credentials
    oleUsername, olePassword = map(
        lambda x: urllib.parse.unquote(x),
        (keyring.get_password("system", "SaintsPayOLECredentials") or "&").split("&"),
    )

    group = DispatchGroup()

    if not (oleUsername and olePassword):
        group.enter()

        def prompt_login():
            global oleUsername, olePassword

            oleUsername = None
            olePassword = None

            def callback(username, password):
                global oleUsername, olePassword

                oleUsername = username
                olePassword = password

                if not (oleUsername and olePassword):

                    def callback():
                        messagebox.showerror(
                            "Error",
                            "You must login to the OLE to use Saints Pay.",
                            parent=root,
                        )

                        prompt_login()

                    root.after(10, callback)
                    return

                keyring.set_password(
                    "system",
                    "SaintsPayOLECredentials",
                    urllib.parse.quote(oleUsername)
                    + "&"
                    + urllib.parse.quote(olePassword),
                )

                group.leave()

            ui.ole_login.Window(root, callback)

        prompt_login()

    def callback():
        print("Got OLE Credentials: ", oleUsername, olePassword)

        # try:
        #     ole = OLE(oleUsername, olePassword)
        # except OLE.Error as e:
        #     messagebox.showerror("Error", str(e), parent=root)
        #     prompt_login()
        #     return

        def callback():
            # TODO later: Fetch from firebase
            return

        ui.scanner_setup.Window(root, lambda: callback)

    group.notify(callback)


if __name__ == "__main__":
    root.after(10, startup)
    root.mainloop()
