import datetime
from functools import partial
from tkinter import (
    Toplevel, Frame, Label, Button, Entry, StringVar, Scrollbar, Canvas,
    messagebox as tkmb
)

from util.const import pkw
from util.routine import floatify, validate_date


class MeasurementsTL(Toplevel):

    def __init__(self, master, points=(), dates=(), empties=1, **kw):
        assert len(points) == len(dates)
        super().__init__(master, **kw)
        self.title("Pontok bevitele")
        self.rowframe = None
        self._build_interface()
        self.rowframe.add_rows(points, dates, empties)
        self.points = list(points)
        self.dates = list(dates)

    def _build_interface(self):
        mf = Frame(self)
        mf.pack(side="left", **pkw)

        self.rowframe = RowFrame(mf)
        self.rowframe.grid(row=1, column=0, columnspan=2, sticky="news")
        Button(mf, text="Új sor...", command=lambda: self.rowframe.add_rows(empties=1)
               ).grid(row=2, column=0, columnspan=2, sticky="news")
        Button(mf, text="Mégse", command=self.destroy
               ).grid(row=3, column=0, sticky="news")
        Button(mf, text="OK", command=self.pull_data
               ).grid(row=3, column=1, sticky="news")

    def pull_data(self):
        for vvar, dvar in self.rowframe.variables:
            if vvar.get() == "":
                continue
            datestr = dvar.get()
            if datestr[-1] == ".":
                datestr = datestr[:-1]
            if not validate_date(datestr):
                tkmb.showerror(
                    "Beviteli hiba!",
                    "Helytelen dátum kitöltés!\nA helyes formátum: ÉÉÉÉ.HH.NN",
                    master=self
                )
                return
            dvar.set(datestr)
            self.dates.append(datestr)
            self.points.append(floatify(vvar))
        self.destroy()


class RowFrame(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.variables = []
        self._build_canvas_and_scrollbar()
        self._build_dataframe()

    def _build_canvas_and_scrollbar(self):
        self.cv = Canvas(self, bd=0, highlightthickness=0)
        sb = Scrollbar(self.cv, orient="vertical")
        self.cv.configure(yscrollcommand=sb.set)
        sb.configure(command=self.cv.yview)
        self.cv.pack(**pkw)
        sb.pack(side="right", fill="y", expand=True)
        return self.cv

    def _build_dataframe(self):
        self.dataframe = Frame(self.cv)
        self.dataframe.pack(side="right", **pkw)
        Label(self.dataframe, text="Mért érték", bd=1, relief="ridge",
              font=("Times New Roman", 14)).grid(row=0, column=0, sticky="news")
        Label(self.dataframe, text="Mérés dátuma", bd=1, relief="ridge",
              font=("Times New Roman", 14)).grid(row=0, column=1, sticky="news")

    def add_rows(self, values=(), dates=(), empties=0):
        assert len(values) == len(dates)
        values = list(values) + ["" for _ in range(empties)]
        dates = list(dates) + ["" for _ in range(empties)]
        for value, date in zip(values, dates):
            if not date:
                date = datetime.datetime.now().strftime("%Y.%m.%d")
            self.variables += [(StringVar(value), StringVar(value=date))]
        self.update_rows()

    def update_rows(self):
        self.dataframe.destroy()
        self._build_dataframe()
        for rown, (vvar, dvar) in enumerate(self.variables, start=1):
            ve = Entry(self.dataframe, textvariable=vvar)
            ve.grid(row=rown, column=0, sticky="news")
            de = Entry(self.dataframe, textvariable=dvar)
            de.grid(row=rown, column=1, sticky="news")
            b = Button(self.dataframe, text="-", width=2,
                       command=partial(droprow, rown, self))
            b.grid(row=rown, column=2)


def droprow(rown, frame):
    """This routine can't be converted into a method because of <partial>"""
    if len(frame.variables) <= 1:
        return
    frame.variables.pop(rown)
    frame.update_rows()
