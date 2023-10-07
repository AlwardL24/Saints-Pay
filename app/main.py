from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import askstring
from ttkthemes import ThemedTk
import keyring
import urllib.parse
import ui.dashboard
import ui.ole_login
import ui.scanner_setup
import ui.payment_terminal
import ui.startup
import ui.image_display
import ui.alert
import ui.transaction_filter
import ui.transactions_list
import time
import os
import requests
from utils.dispatch_group import DispatchGroup
import utils.tkinter.messagebox as messagebox
from backend.ole import OLE
import backend.operator
import utils.user_data_directory as udd
import utils.system_sans_font
import math
from PIL import Image, ImageTk


# TODO:
# - consistency: use either all camelCase or all snake_case
# - potentially add a button in payment terminal to "manually enter transaction" and create a window for creating local student
# - add confirmation popup before clearing student cache
# - make closing the startup window close the app
# - make closing the dashboard window close the app, and if other windows are open prompt with a message saying all windows will be closed

# - windows compatibility:
# - make the sort by box on export screen slightly wider
# - make the startup window, export to excel window, and transaction confirmation window slightly taller
# - tri-state not supported in windows anyways, change the tkinter checkbutton to a ttk checkbutton for select all


root = ThemedTk(theme="arc", toplevel=True, className="Saints Pay")
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
    # saints_pay_style_normal_12_tbutton = ttk.Style()
    # saints_pay_style_normal_12_tbutton.configure(
    #     "SaintsPayStyle.Normal.12.TButton",
    #     font=(utils.system_sans_font, 12),
    #     padx=10,
    #     pady=5,
    #     borderless=True,
    # )

    saints_pay_style_font = ttk.Style()
    saints_pay_style_font.configure(
        ".",
        font=(
            utils.system_sans_font.normal,
            int(12 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_l_tlabel = ttk.Style()
    saints_pay_style_l_tlabel.configure(
        "SaintsPayStyle.L.TLabel",
        font=(
            utils.system_sans_font.normal,
            int(14 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_bold_tlabel = ttk.Style()
    saints_pay_style_bold_tlabel.configure(
        "SaintsPayStyle.Bold.TLabel",
        font=(
            utils.system_sans_font.bold,
            int(12 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_boldl_tlabel = ttk.Style()
    saints_pay_style_boldl_tlabel.configure(
        "SaintsPayStyle.BoldL.TLabel",
        font=(
            utils.system_sans_font.bold,
            int(14 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_boldxl_tlabel = ttk.Style()
    saints_pay_style_boldxl_tlabel.configure(
        "SaintsPayStyle.BoldXL.TLabel",
        font=(
            utils.system_sans_font.bold,
            int(24 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_boldxxl_tlabel = ttk.Style()
    saints_pay_style_boldxxl_tlabel.configure(
        "SaintsPayStyle.BoldXXL.TLabel",
        font=(
            utils.system_sans_font.bold,
            int(28 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_l_tbutton = ttk.Style()
    saints_pay_style_l_tbutton.configure(
        "SaintsPayStyle.L.TButton",
        font=(
            utils.system_sans_font.normal,
            int(14 * utils.system_sans_font.size_multiplier),
        ),
    )

    saints_pay_style_l_tentry = ttk.Style()
    saints_pay_style_l_tentry.configure(
        "SaintsPayStyle.L.TEntry",
        font=(
            utils.system_sans_font.normal,
            int(14 * utils.system_sans_font.size_multiplier),
        ),
    )

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

    startup_window.set_loading_text("Setting up database...")

    def callback(_):
        backend.operator.set_operator(operator_name_stringvar.get())

        startup_window.set_loading_text("Getting OLE credentials...")

        # check for OLE login credentials
        oleUsername, olePassword = map(
            lambda x: urllib.parse.unquote(x),
            (keyring.get_password("system", "SaintsPayOLECredentials") or "&").split(
                "&"
            ),
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
                            parent=startup_window,
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

        if not (oleUsername and olePassword):
            prompt_login()

        def callback():
            nonlocal oleUsername, olePassword, prompt_login, startup_window
            global ole

            startup_window.set_loading_text("Logging into the OLE...")

            ole_info_title = None
            ole_info_message = None

            def info_callback(title, message):
                nonlocal ole_info_title, ole_info_message
                ole_info_title = title
                ole_info_message = message

            try:
                ole = OLE(
                    oleUsername,
                    olePassword,
                    info_callback=info_callback,
                )
            except OLE.Error as error:
                if error.retry_in is not None:
                    message = error.message
                    retry_in = error.retry_in

                    alert_window = ui.alert.Window(
                        startup_window,
                        "Error",
                        f"{message}\n\nRetrying in {retry_in} seconds...",
                        "error",
                    )

                    date = time.time()

                    def tick():
                        nonlocal date, message, retry_in
                        if time.time() - date >= retry_in:
                            if alert_window.winfo_exists():
                                alert_window.destroy()
                            callback()
                            return
                        else:
                            if alert_window.winfo_exists():
                                alert_window.set_message(
                                    f"{message}\n\nRetrying in {int(math.ceil(retry_in - (time.time() - date)))} seconds..."
                                )

                        root.after(1000, tick)

                    tick()
                else:
                    messagebox.showerror("Error", str(error), parent=startup_window)
                    keyring.delete_password("system", "SaintsPayOLECredentials")
                    prompt_login()
                return

            def log_out():
                nonlocal oleUsername, olePassword, prompt_login, startup_window
                global ole

                ole = None

                startup_window = ui.startup.Window(root)

                keyring.delete_password("system", "SaintsPayOLECredentials")

                dashboard.destroy()

                prompt_login()

            # ui.scanner_setup.Window(root, lambda: callback)

            startup_window.destroy()

            # temp = ui.transactions_list.Window(root, ole=ole)  ##

            dashboard = ui.dashboard.Window(root, ole, log_out_callback=log_out)  ##

            if ole_info_title and ole_info_message:
                messagebox.showinfo(
                    ole_info_title, ole_info_message, parent=dashboard
                )  ##
                # messagebox.showinfo(ole_info_title, ole_info_message, parent=temp)  ##

        group.notify_permanently(callback)

    # prompt for operator
    operator_name_stringvar = StringVar(value=backend.operator.get_last_operator())
    ui.alert.Window(
        root,
        "Operator",
        "Please enter your operator name.\nThis will appear on transactions you make.",
        callback=callback,
        inputs=[operator_name_stringvar],
    )


if __name__ == "__main__":
    ico = Image.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icon.png")
    )
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(True, photo)
    root.wm_title("Saints Pay")

    # root.tk.call("tk", "scaling", 3.0)

    root.after(10, startup)
    root.mainloop()
