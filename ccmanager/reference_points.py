import datetime
from functools import partial
from statistics import stdev, mean
from tkinter import (
    Toplevel, Frame, Label, Button, Entry, StringVar,
    messagebox as tkmb
)

from backend.util import floatify


class RefPointsTL(Toplevel):

    def __init__(self, master, N, **kw):
        super().__init__(master, **kw)
        self.title("Pontok bevitele")
        self.resizable(None, None)
        self.vars = []
        Label(self, text="Mért érték").grid(row=0, column=0, sticky="news")
        Label(self, text="Mérés dátuma").grid(row=0, column=1, sticky="news")
        self.rowframe = Frame(self)
        self.rowframe.grid(row=1, column=0, columnspan=2)
        Button(self, text="Új sor...", command=self.add_row
               ).grid(row=2, column=0, columnspan=2, sticky="news")
        Button(self, text="Mégse", command=self.destroy
               ).grid(row=3, column=0, sticky="news")
        Button(self, text="OK", command=self.save_and_exit
               ).grid(row=3, column=1, sticky="news")
        self.add_row(N)

    def reposition(self):
        x, y = self.master.winfo_x(), self.master.winfo_y()
        self.update()
        w, h = self.winfo_width(), self.winfo_height()
        dx = x + w//2
        dy = y + h//2
        self.geometry(f"{w}x{h}+{dx}+{dy}")

    def add_row(self, n=1):
        if len(self.vars) >= 15:
            return
        now = datetime.datetime.now().strftime("%Y.%m.%d.")
        newrows = [(StringVar(), StringVar(value=now)) for _ in range(n)]
        self.vars += newrows
        self.update_rows()

    def update_rows(self):
        self.rowframe.destroy()
        self.rowframe = Frame(self)
        self.rowframe.grid(row=1, column=0, columnspan=2)
        for rown, (vvar, dvar) in enumerate(self.vars):
            ve = Entry(self.rowframe, textvariable=vvar)
            ve.grid(row=rown, column=0, sticky="news")
            de = Entry(self.rowframe, textvariable=dvar)
            de.grid(row=rown, column=1, sticky="news")
            b = Button(self.rowframe, text="-", width=2,
                       command=partial(droprow, rown, self))
            b.grid(row=rown, column=2)

    def push_data_upstream(self, average, std):
        print("Pushed upstream!")
        self.master.data["mean"] = average
        self.master.data["std"] = std

    def pull_data(self):
        try:
            data = [[floatify(vvar.get()), dvar.get()]
                    for vvar, dvar in self.vars if vvar.get()]
        except ValueError:
            tkmb.showerror("Értékhiba!", "Helytelen kitöltés!")
            return None
        if len(data) < 2:
            tkmb.showerror("Hiba!", "Legalább három pontra van szükség!")
            return None
        return list(zip(*data))

    def save_and_exit(self):
        ret = self.pull_data()
        if ret is None:
            return
        vals, dates = ret
        self.push_data_upstream(mean(vals), stdev(vals))
        self.destroy()


def droprow(rown, frm):
    print("Dropping row:", rown)
    if len(frm.vars) <= 1:
        return
    frm.vars.pop(rown)
    frm.update_rows()
