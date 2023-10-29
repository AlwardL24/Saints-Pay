def center(win, offset_x=0, offset_y=0):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry(
        "{}x{}+{}+{}".format(
            int(width), int(height), int(x + offset_x), int(y + offset_y)
        )
    )
    win.deiconify()


def center_within_rect(win, rect, resize_window_if_larger=False):
    """
    centers a tkinter window within a rectangle
    :param win: the main window or Toplevel window to center
    :param rect: the rectangle to center within
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width

    if resize_window_if_larger:
        if win_width > rect["width"]:
            win_width = rect["width"]
            width = win_width - 2 * frm_width
        if win_height > rect["height"]:
            win_height = rect["height"]
            height = win_height - titlebar_height - frm_width

    x = rect["x"] + rect["width"] // 2 - win_width // 2
    y = rect["y"] + rect["height"] // 2 - win_height // 2
    win.geometry("{}x{}+{}+{}".format(int(width), int(height), int(x), int(y)))
    win.deiconify()
