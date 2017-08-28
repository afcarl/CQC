import datetime
from tkinter import (
    Toplevel, Frame, Label, Button, Entry, StringVar, messagebox as tkmb
)

from controlchart import Measurements
from util.const import pkw
from util.routine import floatify, validate_date, datefmt


class _MeasurementTLBase(Toplevel):

    def __init__(self, master, measureobj: Measurements, rown, **kw):
        title = kw.pop("title")
        super().__init__(master, **kw)
        self.title(title)
        self.measure = measureobj  # type: Measurements
        self.results = []
        self.rowframe = None
        self.rown = rown
        self.protocol("WM_DELETE_WINDOW", self._exitcallback)

    def _build_interface(self):
        mf = Frame(self)
        mf.pack(side="left", **pkw)

        self.rowframe = _RowFrame(mf, self.rown)
        self.rowframe.grid(row=1, column=0, columnspan=2, sticky="news")

        Button(mf, text="OK", command=self.pull_data
               ).grid(row=3, column=0, columnspan=2, sticky="news")
        return mf

    def _exitcallback(self):
        msg = "Adatok módosultak. Valóban kilép mentés nélkül?"
        if not self.rowframe.saved:
            if not tkmb.askyesno("Figyelem!", msg):
                return
        self.destroy()

    def update_rowframe(self):
        raise NotImplementedError

    def pull_data(self):
        for vvar, dvar, cvar in self.rowframe.variables:
            vval = vvar.get()
            if vval == "":
                continue
            datestr = dvar.get()
            if datestr[-1] == ".":
                datestr = datestr[:-1]
                dvar.set(datestr)
            if not validate_date(datestr):
                tkmb.showerror(
                    "Beviteli hiba!",
                    "Helytelen dátum kitöltés!\nA helyes formátum: ÉÉÉÉ.HH.NN",
                    master=self
                )
                return
            self.results.append([floatify(vval), datestr, cvar.get()])
        self.destroy()

    @property
    def N(self):
        return len(self.measure["value"])


class EditMeasurements(_MeasurementTLBase):

    def __init__(self, master, measure: Measurements, rown=10, **kw):
        super().__init__(master, measure, rown, **kw)
        self.nextbut = None
        self.prevbut = None
        self.page = 0
        self.pages = [(measure["value"][start:start + rown],
                       measure["date"][start:start + rown],
                       measure["comment"][start:start + rown])
                      for start in range(0, self.N, rown)]
        self._build_interface()
        self.update_rowframe()

    def _build_interface(self):
        mf = super()._build_interface()
        self.prevbut = Button(mf, text="Előző", command=lambda: self.pageturn(-1), state="disabled")
        self.prevbut.grid(row=2, column=0, sticky="news")
        self.nextbut = Button(mf, text="Következő", command=lambda: self.pageturn(+1))
        self.nextbut.grid(row=2, column=1, sticky="news")
        if self.N < self.rown:
            self.nextbut.configure(state="disabled")

    def pageturn(self, where):
        self.page += where
        self.update_rowframe()

    def update_rowframe(self):
        self.prevbut.configure(state=("disabled" if not self.page else "active"))
        self.nextbut.configure(state=("disabled" if self.page == len(self.pages)-1 else "active"))
        self.rowframe.display(*self.pages[self.page], datenow=False)


class NewMeasurements(_MeasurementTLBase):

    def __init__(self, master, measureobj: Measurements, rown, **kw):
        super().__init__(master, measureobj, rown, **kw)
        self._build_interface()

    def _build_interface(self):
        mf = super()._build_interface()
        self.rowframe.add_empties(self.rown)
        Button(mf, text="Új sor...", command=lambda: self.rowframe.add_empties(1)
               ).grid(row=2, column=0, columnspan=2, sticky="news")

    def update_rowframe(self):
        self.rowframe.display(datenow=True)


class _RowFrame(Frame):

    def __init__(self, master, maxrow, **kw):
        super().__init__(master, **kw)
        self.maxrow = maxrow
        self.saved = True
        self.variables = []
        self._build_dataframe()

    def _build_dataframe(self):
        lkw = dict(bd=1, relief="ridge", font=("Times New Roman", 14))
        gkw = dict(row=0, sticky="news")
        self.dataframe = Frame(self)
        self.dataframe.pack(side="right", **pkw)
        Label(self.dataframe, text="Mért érték", width=15, **lkw).grid(column=0, **gkw)
        Label(self.dataframe, text="Mérés dátuma", width=15, **lkw).grid(column=1, **gkw)
        Label(self.dataframe, text="Megjegyzés", width=30, **lkw).grid(column=2, **gkw)

    def display(self, values=(), dates=(), comments=(), datenow=True):
        self.reset()
        assert len(values) == len(dates)
        assert len(values) <= self.maxrow
        self.add_rows(values, dates, comments)
        self.add_empties(self.maxrow - len(values), datenow)

    def add_rows(self, values, dates, comments):
        for value, date, comment in zip(values, dates, comments):
            self.variables += [(StringVar(value=value), StringVar(value=date), StringVar(value=comment))]
            self.variables[-1][0].trace("w", self.varchange)
            self.variables[-1][1].trace("w", self.varchange)
            self.variables[-1][2].trace("w", self.varchange)
        self.update_rows()

    def add_empties(self, N, datenow=True):
        datefill = datefmt(datetime.datetime.now()) if datenow else ""
        self.add_rows(
            values=("" for _ in range(N)),
            dates=(datefill for _ in range(N)),
            comments=("" for _ in range(N))
        )

    def update_rows(self):
        self.dataframe.destroy()
        self._build_dataframe()
        for rown, (vvar, dvar, cvar) in enumerate(self.variables, start=1):
            ve = Entry(self.dataframe, textvariable=vvar)
            ve.grid(row=rown, column=0, sticky="news")
            de = Entry(self.dataframe, textvariable=dvar)
            de.grid(row=rown, column=1, sticky="news")
            ce = Entry(self.dataframe, textvariable=cvar)
            ce.grid(row=rown, column=2, sticky="news")

    def reset(self):
        self.variables = []
        self.update_rows()

    # noinspection PyUnusedLocal
    def varchange(self, *args):
        self.saved = False
