import datetime
from tkinter import StringVar


def floatify(string):
    if isinstance(string, StringVar):
        string = string.get()
    if string:
        return float(string.replace(",", "."))
    raise ValueError(f"Cannot floatify {string}!")


def replace_toplevel(master, toplevel, resizeable=False):
    x, y = master.winfo_x(), master.winfo_y()
    toplevel.update()
    w, h = toplevel.winfo_width(), toplevel.winfo_height()
    dx = x + w // 2
    dy = y + h // 2
    toplevel.geometry(f"{w}x{h}+{dx}+{dy}")
    toplevel.resizable(*[resizeable]*2)


def validate_date(datestr):
    try:
        datetime.datetime.strptime(datestr, "%Y.%m.%d")
    except ValueError:
        return False
    return True


def dumpobj(obj, path):
    import pickle
    import gzip
    with gzip.open(path, "wb") as handle:
        pickle.dump(obj, handle)


def loadobj(path):
    import pickle
    import gzip
    with gzip.open(path, "rb") as handle:
        return pickle.load(handle)


def datefmt(datetimeobj):
    return datetime.datetime.strftime(datetimeobj, "%Y.%m.%d")


def repeat(N, **vals):
    return {k: [vals[k] for _ in range(N)] for k in vals if vals[k] is not None}
