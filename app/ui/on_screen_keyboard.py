import tkinter as tk
from tkinter import ttk
import pyautogui
from utils.tkinter.center import center


class Window(tk.Toplevel):
    def __init__(
        self,
        master,
        event_listener=None,
        special_keys={
            "shift": "MODIFIER_SHIFT",
            "caps lock": "MODIFIER_CAPS",
            "backspace": "SPECIAL_BACKSPACE",
            "enter": "SPECIAL_ENTER",
            "tab": "SPECIAL_TAB",
            "": "SPECIAL_SPACE",
            "▴": "SPECIAL_ARROW_UP",
            "◂": "SPECIAL_ARROW_LEFT",
            "▾": "SPECIAL_ARROW_DOWN",
            "▸": "SPECIAL_ARROW_RIGHT",
        },
        keyboard_symbols={
            "␋": "backspace",
            "␉": "tab",
            "␊": "caps lock",
            "␤": "enter",
            "␍": "shift",
            "§": "",
            "¶": '"',
        },
        keyboard=(
            "~†!†@†#†$†%†^†&†*†(†)†_†+†␋†††" + "\n"
            "`†1†2†3†4†5†6†7†8†9†0†-†=†††††" + "\n"
            "␉¦¦¦Q¦W¦E¦R¦T¦Y¦U¦I¦O¦P¦{¦}¦|¦" + "\n"
            "¦¦¦¦q¦w¦e¦r¦t¦y¦u¦i¦o¦p¦[¦]¦\¦" + "\n"
            "␊†††A†S†D†F†G†H†J†K†L†:†¶†␤†††" + "\n"
            "††††a†s†d†f†g†h†j†k†l†;†'†††††" + "\n"
            "␍¦¦¦¦Z¦X¦C¦V¦B¦N¦M¦<¦>¦?¦␍¦¦¦¦" + "\n"
            "¦¦¦¦¦z¦x¦c¦v¦b¦n¦m¦,¦.¦/¦¦¦¦¦¦" + "\n"
            "‡‡‡‡‡‡‡‡§†††††††††††††‡‡‡‡▴†‡‡" + "\n"
            "‡‡‡‡‡‡‡‡††††††††††††††‡‡◂¦▾¦▸¦"
        ),
        window_close_callback=None,
    ):
        tk.Toplevel.__init__(self, master)

        self.title("On Screen Keyboard")

        self.attributes("-topmost", True)

        style = ttk.Style()
        self.configure(bg="gray99")
        style.configure(
            "OnScreenKeyboard.TButton", background="azure", foreground="black"
        )

        is_shift = False
        is_caps = False

        def press(num):
            nonlocal is_shift, is_caps

            if num == "MODIFIER_SHIFT":
                is_shift = not is_shift
                update()
                return

            if num == "MODIFIER_CAPS":
                is_caps = is_shift = not is_caps
                update()
                return

            if num.startswith("SPECIAL_"):
                event_listener({"type": "SPECIAL", "key": num.replace("SPECIAL_", "")})
                return

            # exp = exp + str(num)
            # equation.set(exp)
            print("pressing ", num)

            event_listener({"type": "KEY", "key": num})

            if (not is_caps) and is_shift:
                is_shift = False
                update()

        keyboard_lines = keyboard.splitlines()
        print(keyboard_lines)
        number_rows = len(keyboard_lines)
        number_cols = max([len(line) for line in keyboard_lines])

        self.columnconfigure(list(range(number_cols)), minsize=35)
        self.rowconfigure(list(range(number_rows)), minsize=35)

        self.geometry(f"{number_cols * 35}x{number_rows * 35}")
        self.resizable(False, False)

        def press_function_constructor(num):
            return lambda: press(num)

        def draw(keyboard):
            tokens = []

            for line in keyboard.splitlines():
                chars = []
                for char in line:
                    chars.append(char)
                tokens.append(chars)

            for y, line in enumerate(tokens):
                for x, token in enumerate(line):
                    if token in ["†", "¦", "‡"]:
                        continue

                    text = ""

                    if token in keyboard_symbols:
                        text = keyboard_symbols[token]
                    else:
                        text = token

                    width = 1
                    height = 1

                    padding_token = ""

                    while x + width < len(line):
                        if line[x + width] not in ["†", "¦", "‡"]:
                            break
                        if padding_token == "":
                            padding_token = line[x + width]
                        if padding_token != line[x + width]:
                            break

                        width += 1

                    while y + height < len(tokens):
                        if len(tokens[y + height]) <= x + width - 1:
                            break
                        if tokens[y + height][x + width - 1] not in ["†", "¦", "‡"]:
                            break
                        if padding_token == "":
                            padding_token = tokens[y + height][x + width - 1]
                        if padding_token != tokens[y + height][x + width - 1]:
                            break

                        height += 1

                    if height > 1 and tokens[y + 1][x] not in ["†", "¦", "‡"]:
                        _text = ""
                        if tokens[y + 1][x] in keyboard_symbols:
                            _text = keyboard_symbols[tokens[y + 1][x]]
                        else:
                            _text = tokens[y + 1][x]
                        text = text if is_shift else _text
                        tokens[y + 1][x] = padding_token

                    _press = text

                    if text in special_keys:
                        _press = special_keys[text]

                        if special_keys[text] == "MODIFIER_SHIFT":
                            text = f"{'●' if is_shift else '○'}   " + text
                        elif special_keys[text] == "MODIFIER_CAPS":
                            text = f"{'●' if is_caps else '○'}   " + text

                    button = ttk.Button(
                        self,
                        style="OnScreenKeyboard.TButton",
                        text=text,
                        command=press_function_constructor(_press),
                        width=1,
                    )
                    button.grid(
                        sticky="NSEW",
                        row=y,
                        column=x,
                        columnspan=width,
                        rowspan=height,
                    )

        def update():
            # remove all widgets
            for widget in self.winfo_children():
                widget.destroy()

            # redraw
            draw(keyboard)

        update()

        if window_close_callback is not None:

            def closed():
                window_close_callback()
                self.destroy()

            self.protocol("WM_DELETE_WINDOW", closed)

        center(self)
