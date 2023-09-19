from tkinter import *
from utils.tkinter.smooth_scrolled_text import SmoothScrolledText

root = Tk()

# frame = Frame(root)
# frame.pack()

# vbar = Scrollbar(frame)
# vbar.pack(side=RIGHT, fill=Y)

# text = Text(frame, width=15, yscrollcommand=vbar.set)
# text.pack(side=LEFT, fill=BOTH, expand=True)

# vbar["command"] = text.yview

box = SmoothScrolledText(root, width=15)
box.pack()

for i in range(20):
    frame = Frame()
    label = Label(frame, text=f"item {i}")
    label.pack(side=LEFT)
    button = Button(frame, text="click")
    button.pack(side=LEFT)
    box.window_create(END, window=frame)
    box.insert(END, "\n")

box.configure(state="disabled")

# def scroll(event):
#     print(event.delta)
#     text.yview_moveto(text.yview()[0] + vbar.delta(0, -event.delta * 2))
#     return "break"


# root.bind(
#     "<MouseWheel>",
#     scroll,
# )
# text.bind("<MouseWheel>", scroll)
# vbar.bind("<MouseWheel>", scroll)

root.mainloop()
