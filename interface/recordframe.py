from tkinter import Frame, Label, Button, Entry, messagebox as tkmb
from tkinter.ttk import Combobox
from datetime import datetime

from .measurements import NewMeasurements
from controlchart.parameter import MethodRecord, ParameterRecord, CCRecord, Measurements
from util.routine import validate_date, datefmt, floatify


def _throw(errmsg):
    tkmb.showerror("Figyelem!", errmsg)


class _StaffSelector(Combobox):

    def __init__(self, master, **kw):
        self.dbifc = master.dbifc
        values = [v[0] for v in master.dbifc.query(
            "SELECT name FROM Staff WHERE level == 20 ORDER BY name;")]
        super().__init__(master, width=(master.width*2)-2, values=values, **kw)
        self.fill()

    def fill(self, refname=None):
        del refname
        name = self.master.results["staff_id"]
        data = self.dbifc.get_username(name) if name else self.dbifc.current_user()
        self.set(data)

    def get(self):
        return self.master.dbifc.get_tasz(super().get())


class _RecEntry(Entry):

    def __init__(self, master, **kw):
        super().__init__(master, width=master.width*2, fg="black", bg="white",
                         disabledforeground="black", **kw)

    def fill(self, refname):
        data = self.master.results[refname]
        self.delete(0, "end")
        self.insert(0, data if data else "")


class _DateEntry(_RecEntry):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)

    def fill(self, refname):
        date = self.master.results[refname]
        self.delete(0, "end")
        self.insert(0, datefmt(datetime.now()) if not date else date)


class _Record(Frame):

    _title = ""
    _validorz = ()
    _refnames = ()
    _nicenames = ()
    _wtypes = ()
    width = 20

    def __init__(self, master, dbifc, resultobj=None, **kw):
        super().__init__(master, **kw)
        self.dbifc = dbifc
        self.empty = not bool(resultobj)
        self.results = {
            "módszer": MethodRecord, "paraméter": ParameterRecord, "kontroll diagram": CCRecord
        }[self._title]() if resultobj is None else resultobj
        Label(self, text=f"{self._title.capitalize()} adatok", font=("Times New Roman", 14),
              bd=2, relief="raised").grid(row=0, column=0, columnspan=2, sticky="news")
        for i, tx in enumerate(self._nicenames, start=1):
            Label(self, text=tx, justify="left", anchor="w", width=self.width
                  ).grid(row=i, column=0, sticky="nse")
        self.w = {k: v(self) for k, v in zip(self._refnames, self._wtypes)}

        for i, wn in enumerate(self._refnames, start=1):
            self.w[wn].grid(row=i, column=1)

        if not self.empty:
            self.fill()

    def fill(self):
        for rn, w in self.w.items():
            w.fill(rn)

    def _reset_widget(self, wname):
        self.w[wname].delete(0, "end")
        self.w[wname].focus_set()

    def check(self):
        for validor in self._validorz:
            if not validor(self):
                return None
        self.results.incorporate({k: self.w[k].get() for k in self._refnames})
        return self.results

    def lock(self):
        for w in self.w.values():
            w.configure(state="disabled", foreground="black")

    def unlock(self):
        for w in self.w.values():
            w.configure(state="normal", foreground="black")


class MethodFrame(_Record):

    _title = "módszer"
    _refnames = "name", "mnum", "akkn", "staff_id"
    _nicenames = "Megnevezés", "Szám", "Akkred szám", "Felelős"
    _wtypes = _RecEntry, _RecEntry, _RecEntry, _StaffSelector

    def _valid_name(self):
        valid = bool(self.w["name"].get())
        if not valid:
            _throw("Nevet kötelező megadni!")
            self.w["name"].focus_set()
        return valid

    def _valid_mnum(self):
        err = "A módszer száma pozitív egész!"
        mnum = self.w["mnum"].get()
        try:
            mnum = int(mnum)
            if mnum <= 0:
                raise RuntimeError
        except ValueError or RuntimeError:
            _throw(err)
            self._reset_widget("mnum")
            return False
        return True

    def _valid_akkn(self):
        akkn = self.w["akkn"].get()
        err = "Helytelen akkreditációs azonosító formátum! Helyesen: pl. A/13"
        s = akkn.split("/")
        if "/" not in akkn or len(s) != 2 or not s[1].isdigit():
            _throw(err)
            self._reset_widget("akkn")
            return False
        return True

    _validorz = _valid_name, _valid_mnum, _valid_akkn

    def check(self):
        if super().check() is None:
            return None
        self.results["staff_id"] = self.w["staff"].get()
        return self.results


class ParamFrame(_Record):

    _title = "paraméter"
    _refnames = "name", "dimension"
    _nicenames = "Megnevezés", "Mértékegység"
    _wtypes = _RecEntry, _RecEntry

    def _valid_name(self):
        assert self.results.upstream_id is not None
        name = self.w["name"].get()
        if name:
            got = self.dbifc.query("SELECT id FROM Parameter WHERE method_id == ? AND name == ?",
                                   [self.results.upstream_id, name])
            if not got:
                return True
            _throw(f"{name} nevű paraméter már van ehhez a módszerhez!")
        else:
            _throw("Nevet kötelező megadni!")
        self.w["name"].focus_set()
        return False

    _validorz = (_valid_name,)


class CCFrame(_Record):

    _title = "kontroll diagram"
    _refnames = "startdate", "staff_id", "refmaterial", "comment", "refmean", "refstd", "uncertainty"
    _nicenames = "Felvéve (dátum)", "Felelős", "Anyagminta", "Megjegyzés", "Átlag", "Szórás", "Mérési bizonytalanság"
    _wtypes = _DateEntry, _StaffSelector, _RecEntry, _RecEntry, _RecEntry, _RecEntry, _RecEntry

    def __init__(self, master, dbifc, **kw):
        super().__init__(master, dbifc, **kw)
        cols, rows = self.grid_size()
        self.refmeasure_button = Button(
            self, text="Átlag, szórás számítása", command=self._calc_stat
        )
        self.refmeasure_button.grid(row=rows, column=0, columnspan=cols, sticky="news")

    def _calc_stat(self):
        reftl = NewMeasurements(self, Measurements(globref=True), rown=5, title="Referenciamérések bevitele")
        self.wait_window(reftl)
        mu, sigma = reftl.measure.stats()
        self.results["refmean"], self.results["refstd"] = mu, sigma
        self.fill()

    def _valid_startdate(self):
        startdate = self.w["startdate"].get()
        v = validate_date(startdate)
        if not v:
            _throw("Helytelen dátum formátum. Helyesen: ÉÉÉÉ.HH.NN")
            self.w["startdate"].delete(0, "end")
            self.w["startdate"].insert(0, datefmt(datetime.now()))
            self.w["startdate"].focus_set()
        return v

    def _valid_refmaterial(self):
        valid = bool(self.w["refmaterial"].get())
        if not valid:
            _throw("Anyagminta azonosítót kötelező megadni!")
            self.w["refmaterial"].focus_set()
        return valid

    def _valid_unique(self):
        startdate = self.w["startdate"].get()
        refmaterial = self.w["refmaterial"].get()
        sqlcmd = "SELECT id FROM Controll_diagram WHERE startdate == ? AND refmaterial == ?"
        valid = bool(len(self.dbifc.query(sqlcmd, [startdate, refmaterial])))
        if not valid:
            _throw(f"{startdate} dátummal {refmaterial} anyagmintára már létezik kontroll diagram!")
        return valid

    def _validate_float(self, name, refstr):
        refstring = self.w[refstr].get()
        try:
            floatify(refstring)
        except ValueError:
            _throw(f"{name} értéket kötelező megadni számként!")
            self.w[refstr].focus_set()
            return False
        return True

    def _valid_refmean(self):
        return self._validate_float("Átlag", "refmean")

    def _valid_refstd(self):
        return self._validate_float("Szórás", "refstd")

    _validorz = (_valid_startdate, _valid_refmaterial, _valid_refmean, _valid_refstd)

    def check(self):
        if super().check() is None:
            return None
        return self.results

    def lock(self):
        super().lock()
        self.refmeasure_button.configure(state="disabled")

    def unlock(self):
        super().unlock()
        self.refmeasure_button.configure(state="normal")
