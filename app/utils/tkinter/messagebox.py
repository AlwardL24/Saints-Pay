import ui.alert


def showerror(title, message, parent=None):
    ui.alert.Window(parent, title, message, "error").wait_window()


def showwarning(title, message, parent=None):
    ui.alert.Window(parent, title, message, "warning").wait_window()


def showinfo(title, message, parent=None):
    ui.alert.Window(parent, title, message, "info").wait_window()
