from tkinter import StringVar


def floatify(string):
    if isinstance(string, StringVar):
        string = string.get()
    if string:
        return float(string.replace(",", "."))
    return None


def replace_toplevel(master, toplevel, resizeable=False):
    x, y = master.winfo_x(), master.winfo_y()
    toplevel.update()
    w, h = toplevel.winfo_width(), toplevel.winfo_height()
    dx = x + w // 2
    dy = y + h // 2
    toplevel.geometry(f"{w}x{h}+{dx}+{dy}")
    toplevel.resizable(*[resizeable]*2)
