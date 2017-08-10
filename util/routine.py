from tkinter import StringVar


def floatify(string):
    if isinstance(string, StringVar):
        string = string.get()
    if string:
        return float(string.replace(",", "."))
    return None