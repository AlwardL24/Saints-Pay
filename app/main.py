from tkinter import *
from tkinter import messagebox
import keyring
import urllib.parse
import ui
import time
import os
import requests
from utils.dispatch_group import DispatchGroup
from backend.ole import OLE
import utils.user_data_directory as udd


root = Tk()
root.withdraw()


ole = None


def get_size_of_dir(dir: str) -> int:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def startup():
    startup_window = ui.startup.Window(root)

    # if the size of the student image cache is greater than 5MB, delete the oldest images until it is less than 5MB
    image_cache_directory = udd.get_user_data_dir(
        ["SaintsPay", "student-data-cache", "images"]
    )

    if not os.path.exists(image_cache_directory):
        os.makedirs(image_cache_directory)

    if get_size_of_dir(image_cache_directory) > 5 * 1024 * 1024:
        startup_window.set_loading_text("Cleaning up student image cache...")

    while get_size_of_dir(image_cache_directory) > 5 * 1024 * 1024:
        oldest_file = None
        oldest_file_time = None

        for filename in os.listdir(image_cache_directory):
            path = os.path.join(image_cache_directory, filename)
            if oldest_file is None:
                oldest_file = path
                oldest_file_time = os.path.getmtime(path)
            else:
                file_time = os.path.getmtime(path)
                if file_time < oldest_file_time:
                    oldest_file = path
                    oldest_file_time = file_time

        os.remove(oldest_file)

    startup_window.set_loading_text("Getting OLE credentials...")

    # check for OLE login credentials
    oleUsername, olePassword = map(
        lambda x: urllib.parse.unquote(x),
        (keyring.get_password("system", "SaintsPayOLECredentials") or "&").split("&"),
    )

    group = DispatchGroup()

    def prompt_login():
        group.enter()

        nonlocal oleUsername, olePassword

        oleUsername = None
        olePassword = None

        def callback(username, password):
            nonlocal oleUsername, olePassword

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
                urllib.parse.quote(oleUsername) + "&" + urllib.parse.quote(olePassword),
            )

            group.leave()

        ui.ole_login.Window(root, callback)

    if not (oleUsername and olePassword):
        prompt_login()

    def callback():
        nonlocal oleUsername, olePassword, prompt_login, startup_window
        global ole

        startup_window.set_loading_text("Logging into the OLE...")

        try:
            ole = OLE(
                oleUsername,
                olePassword,
                warning_callback=lambda title, message: messagebox.showwarning(
                    title, message, parent=root
                ),
            )
        except OLE.Error as e:
            messagebox.showerror("Error", str(e), parent=root)
            keyring.delete_password("system", "SaintsPayOLECredentials")
            prompt_login()
            return

        # ui.scanner_setup.Window(root, lambda: callback)

        startup_window.destroy()

        ui.dashboard.Window(root, lambda: ui.payment_terminal.Window(root, ole=ole))

    group.notify_permanently(callback)


if __name__ == "__main__":
    root.after(10, startup)
    root.mainloop()
