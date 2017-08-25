import datetime
from tkinter import (
    Toplevel, Frame, Label, Button, Entry, StringVar,
    messagebox as tkmb
)

from controlchart import ControlChart

from util.const import pkw
from util.routine import floatify, validate_date


class MeasurementsTL(Toplevel):

    def __init__(self, master, ccobj: ControlChart, mode, rowN=10, **kw):
        title = kw.pop("title", "Pontok szerkesztése, bevitele")
        super().__init__(master, **kw)
        self.title(title)
        self.ccobj = ccobj
        self.results = []
        self.rowframe = None
        self.rowN = rowN
        self.page = 0
        self.pages = [(ccobj.measure["value"][start:start + rowN],
                       ccobj.measure["date"][start:start+rowN],
                       ccobj.measure["comment"][start:start+rowN])
                      for start in range(0, len(ccobj.values), rowN)]
        self._build_interface(mode=mode)
        self._turnpage()
        self.protocol("WM_DELETE_WINDOW", self._exitcallback)

    def _build_interface(self, mode):
        mf = Frame(self)
        mf.pack(side="left", **pkw)

        self.rowframe = RowFrame(mf, self.rowN)
        self.rowframe.grid(row=1, column=0, columnspan=2, sticky="news")

        if mode == "turnable":
            self.prevbut = Button(mf, text="Előző", command=self.prevpage, state="disabled")
            self.prevbut.grid(row=2, column=0, sticky="news")
            self.nextbut = Button(mf, text="Következő", command=self.nextpage)
            self.nextbut.grid(row=2, column=1, sticky="news")
        elif mode == "expandable":
            Button(mf, text="Új sor...", command=self.rowframe.add_empties(1))
        if self.N < self.rowN and mode == "turnable":
            self.nextbut.configure(state="disabled")

        Button(mf, text="OK", command=self.pull_data
               ).grid(row=3, column=0, columnspan=2, sticky="news")

    def nextpage(self):
        self.page += 1
        self._turnpage()

    def prevpage(self):
        self.page -= 1
        self._turnpage()

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

    def _turnpage(self):
        self.prevbut.configure(state=("disabled" if not self.page else "active"))
        self.nextbut.configure(state=("disabled" if self.page == len(self.pages)-1 else "active"))
        self.rowframe.display(*self.pages[self.page])

    def _exitcallback(self):
        msg = "Adatok módosultak. Valóban kilép mentés nélkül?"
        if not self.rowframe.saved:
            if not tkmb.askyesno("Figyelem!", msg):
                return
        self.destroy()

    @property
    def N(self):
        return len(self.ccobj.values)


class RowFrame(Frame):

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

    def display(self, values=(), dates=(), comments=()):
        self.reset()
        assert len(values) == len(dates)
        assert len(values) <= self.maxrow
        self.add_rows(values, dates, comments)
        self.add_empties(self.maxrow - len(values))

    def add_rows(self, values, dates, comments):
        for value, date, comment in zip(values, dates, comments):
            self.variables += [(StringVar(value=value), StringVar(value=date), StringVar(value=comment))]
            self.variables[-1][0].trace("w", self.varchange)
            self.variables[-1][1].trace("w", self.varchange)
            self.variables[-1][2].trace("w", self.varchange)
        self.update_rows()

    def add_empties(self, N):
        now = datetime.datetime.now().strftime("%Y.%m.%d")
        self.add_rows(
            values=("" for _ in range(N)),
            dates=(now for _ in range(N)),
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
