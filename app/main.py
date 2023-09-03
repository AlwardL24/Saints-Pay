from tkinter import *
from tkinter import messagebox
import user_data_directory as udd
import keyring
import urllib.parse
import ui.startup
import ui.ole_login
import ui.scanner_setup
import time
import os
import urllib.request
from utils.dispatch_group import DispatchGroup


root = Tk()
root.withdraw()

def download_image(user_id):
    # Create the folder != exists
    if not os.path.exists('images'):
        os.makedirs('images')

    image_filename = f'user_{user_id}.jpg'
    image_path = os.path.join('images', image_filename)

    if not os.path.exists(image_path):
        img_url = f"https://ole.saintkentigern.com/portrait.php?id={user_id}&size=constrain200"
        urllib.request.urlretrieve(img_url, image_path)
        print(f"Image downloaded and saved as {image_path}")
    else:
        print("Image already exists")

    return

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
        #print("Got OLE Credentials: ", oleUsername, olePassword)
        user_id = input("Enter user id: ")
        download_image(user_id)
        def callback():
            # TODO later: Fetch from firebase

            # Sign into the OLE

            

            return


        ui.scanner_setup.Window(root, lambda: callback)

    group.notify(callback)

if __name__ == "__main__":
    root.after(10, startup)
    root.mainloop()
