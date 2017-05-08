from tkinter import Frame, Label, Button, Entry, StringVar

import datetime
from functools import partial


class RefPointsFrame(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.widgets = []
        Label(self, text="Mért érték").grid(row=0, column=0, sticky="news")
        Label(self, text="Mérés dátuma").grid(row=0, column=1, sticky="news")
        self.rowframe = Frame(self)
        self.rowframe.grid(row=1, column=0, columnspan=2)
        Button(self, text="Új sor...", command=self.add_row
               ).grid(row=2, column=0, columnspan=2)
        self.add_row(5)

    def add_row(self, n=1):
        if len(self.widgets) >= 15:
            return
        now = datetime.datetime.now().strftime("%Y.%m.%d.")
        newrows = [(StringVar(), StringVar(value=now)) for _ in range(n)]
        self.widgets += newrows
        self.update_rows()

    def delete_row(self, i):
        print("Dropping row:", i)
        if len(self.widgets) <= 1:
            return
        self.widgets.pop(i)
        self.update_rows()

    def update_rows(self):
        self.rowframe.destroy()
        self.rowframe = Frame(self)
        self.rowframe.grid(row=1, column=0, columnspan=2)
        for rown, (vvar, dvar) in enumerate(self.widgets):
            ve = Entry(self.rowframe, textvariable=vvar)
            ve.grid(row=rown, column=0, sticky="news")
            de = Entry(self.rowframe, textvariable=dvar)
            de.grid(row=rown, column=1, sticky="news")
            b = Button(self.rowframe, text="-", width=2,
                       command=partial(droprow, rown, self))
            b.grid(row=rown, column=2)


def droprow(rown, frm):
    print("Dropping row:", rown)
    if len(frm.widgets) <= 1:
        return
    frm.widgets.pop(rown)
    frm.update_rows()


if __name__ == '__main__':
    from tkinter import Tk
    root = Tk()
    frame = RefPointsFrame(root)
    frame.pack()
    root.mainloop()
