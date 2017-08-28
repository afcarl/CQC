from tkinter import Toplevel, Label, Button, Entry, messagebox as tkmb
from tkinter.ttk import Combobox
from datetime import datetime

from controlchart.parameter import MethodRecord, ParameterRecord, CCRecord
from util.routine import validate_date, datefmt, floatify


def _throw(errmsg):
    tkmb.showerror("Figyelem!", errmsg)


class _StaffSelector(Combobox):
    def __init__(self, master, w, **kw):
        values = [v[0] for v in master.dbifc.query("SELECT name FROM Staff WHERE level == 20 ORDER BY name;")]
        super().__init__(master, width=w*2-2, values=values, **kw)
        self.set(master.dbifc.current_user())


class _RecEntry(Entry):
    def __init__(self, master, w, **kw):
        super().__init__(master, width=w*2-2, **kw)


class _DateEntry(_RecEntry):
    def __init__(self, master, w, **kw):
        super().__init__(master, w, **kw)
        self.insert(0, datefmt(datetime.now()))


class _NewRecord(Toplevel):

    _title = ""
    _validorz = ()
    _refnames = ()
    _nicenames = ()
    _wtypes = ()
    _w = 15

    def __init__(self, master, dbifc, ID=None, **kw):
        super().__init__(master, **kw)
        self.dbifc = dbifc
        self.labels = []
        self.results = self._get_resultobj(ID)
        i = 1
        Label(self, text=f"Új {self._title} regisztrálása", width=self._w, font=("Times New Roman", 14)
              ).grid(row=0, column=0, columnspan=2, sticky="news")
        for i, tx in enumerate(self._nicenames, start=1):
            self.labels.append(Label(self, text=tx, justify="left", anchor="w", width=self._w))
            self.labels[-1].grid(row=i, column=0, sticky="nse")
        self.w = {k: v(self) for k, v in zip(self._refnames, self._wtypes)}

        for i, wn in enumerate(self._refnames, start=1):
            self.w[wn].grid(row=i, column=1)

        Button(self, text="Kész", command=self.done).grid(row=i+1, column=1, sticky="news")
        Button(self, text="Mégse", command=self.destroy).grid(row=i+1, column=0, sticky="news")

    def _get_resultobj(self, ID):
        raise NotImplementedError

    def _reset_widget(self, wname):
        self.w[wname].delete(0, "end")
        self.w[wname].focus_set()

    def done(self):
        for validor in self._validorz:
            if not validor():
                return
        self.results.incorporate({k: self.w[k].get() for k in ("name", "mnum", "akkn")})
        print(self.results.data)
        self.destroy()


class NewMethod(_NewRecord):

    _title = "módszer"
    _refnames = "name", "mnum", "akkn", "staff"
    _nicenames = "Megnevezés", "Szám", "Akkred szám", "Felelős"
    _wtypes = _RecEntry, _RecEntry, _RecEntry, _StaffSelector

    def _get_resultobj(self, ID=None):
        return MethodRecord()

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
        except Exception as E:
            del E
            _throw(err)
            self._reset_widget("mnum")
            return False
        return True

    def _valid_akkn(self):
        akkn = self.w["akkn"].get()
        err = "Helytelen akkreditációs azonosító forma! Helyesen: pl. A/13"
        s = akkn.split("/")
        if "/" not in akkn or len(s) != 2 or not s[1].isdigit():
            _throw(err)
            self._reset_widget("akkn")
            return False
        return True

    _validorz = _valid_name, _valid_mnum, _valid_akkn

    def done(self):
        super().done()
        self.results["staff_id"] = self.dbifc.get_tasz(self.w["staff"].get())


class NewParam(_NewRecord):

    _title = "paraméter"
    _refnames = "name", "dimension"
    _nicenames = "Megnevezés", "Mértékegység"
    _wtypes = _RecEntry, _RecEntry

    def _get_resultobj(self, ID):
        return ParameterRecord.from_values(dict(method_id=ID))

    def _valid_name(self):
        name = self.w["name"].get()
        valid = bool(name)
        if not valid:
            _throw("Nevet kötelező megadni!")
            self.w["name"].focus_set()
        else:
            self.dbifc.x("SELECT id FROM Parameter WHERE method_id == ? AND name == ?",
                         [self.results["method_id"], name])
            if self.dbifc.c.fetchone() is not None:
                _throw("{name} nevű paraméter már van ehhez a módszerhez!")
                return False
        return valid

    _validorz = (_valid_name,)

    def _reset_widget(self, wname):
        self.w[wname].delete(0, "end")
        self.w[wname].focus_set()

    def done(self):
        for validor in self._validorz:
            if not validor(self):
                return
        self.results.incorporate({k: self.w[k].get() for k in ("name", "dimension")})
        print(self.results.data)
        self.destroy()


class NewCC(_NewRecord):

    _title = "kontroll diagram"
    _refnames = "startdate", "staff", "refmaterial", "comment", "refmean", "refstd", "uncertainty"
    _nicenames = "Felvéve (dátum)", "Felelős", "Anyagminta", "Megjegyzés", "Átlag", "Szórás", "Mérési bizonytalanság"
    _wtypes = _DateEntry, _StaffSelector, _RecEntry, _RecEntry, _RecEntry, _RecEntry, _RecEntry
    _w = 20

    def _get_resultobj(self, ID):
        return CCRecord.from_values(dict(parameter_id=ID))

    def _valid_startdate(self):
        startdate = self.w["startdate"].get()
        v = validate_date(startdate)
        if not v:
            tkmb.showerror("Figyelem!", "Helytelen dátum formátum. Helyesen: ÉÉÉÉ.HH.NN")
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

    def _validate_floatvalue(self, name, refstr):
        err = f"{name} értéket kötelező megadni!"
        refmean = self.w[refstr].get()
        if not refmean:
            _throw(err)
            return False
        try:
            floatify(refmean)
        except Exception as E:
            del E
            _throw(err)
            return False
        return True

    def _valid_refmean(self):
        v = self._validate_floatvalue("Átlag", "refmean")
        if not v:
            self.w["refmean"].focus_set()
        return v

    def _valid_refstd(self):
        v = self._validate_floatvalue("Szórás", "refstd")
        if not v:
            self.w["refstd"].focus_set()
        return v

    _validorz = _valid_startdate, _valid_refmaterial, _valid_refmean, _valid_refstd

    def done(self):
        for validor in self._validorz:
            if not validor(self):
                return
        self.results.incorporate({k: self.w[k].get() for k in ("name", "dimension")})
        print(self.results.data)
        self.destroy()


if __name__ == '__main__':
    from tkinter import Tk
    from dbconnection import DBConnection
    tk = Tk()
    tl = NewCC(tk, DBConnection(), 1)
    tk.mainloop()
