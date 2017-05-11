from tkinter import Frame, Label, Entry


def tktable(master, fields, tkvars, lcnf=None, ecnf=None, container=None):
    lcnf = {} if lcnf is None else lcnf
    ecnf = {} if ecnf is None else ecnf
    container = Frame(master) if container is None else container
    for i, (fld, var) in enumerate(zip(fields, tkvars)):
        Label(container, text=fld, **lcnf).grid(row=i, column=0, sticky="news")
        Entry(container, textvariable=var, **ecnf).grid(row=i, column=1, sticky="news")
    return container
