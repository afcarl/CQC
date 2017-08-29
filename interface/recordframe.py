from tkinter import Frame, Label, Button, Entry, messagebox as tkmb
from tkinter.ttk import Combobox
from datetime import datetime

from controlchart.parameter import MethodRecord, ParameterRecord, CCRecord
from util.routine import validate_date, datefmt, floatify


def _throw(errmsg):
    tkmb.showerror("Figyelem!", errmsg)


def _StaffSelector(master, **kw):
    values = [v[0] for v in master.dbifc.query(
        "SELECT name FROM Staff WHERE level == 20 ORDER BY name;")]
    cb = Combobox(master, width=(master.width*2)-4, values=values, **kw)
    cb.set(master.dbifc.current_user())
    return cb


def _RecEntry(master, **kw):
    return Entry(master, width=master.width*2-2, disabledforeground="black", **kw)


def _DateEntry(master, **kw):
    e = _RecEntry(master, **kw)
    e.insert(0, datefmt(datetime.now()))
    return e


class _Record(Frame):

    _title = ""
    _validorz = ()
    _refnames = ()
    _nicenames = ()
    _wtypes = ()
    width = 20

    def __init__(self, master, dbifc, uID=None, newcb=None, resultobj=None, **kw):
        super().__init__(master, **kw)
        self.dbifc = dbifc
        self.upstream_ID = uID
        if resultobj is None:
            self.results = {"módszer": MethodRecord, "paraméter": ParameterRecord,
                            "kontroll diagram": CCRecord}[self._title]()
        Label(self, text=f"{self._title.capitalize()} adatok", font=("Times New Roman", 14),
              bd=2, relief="raised").grid(row=0, column=0, columnspan=2, sticky="news")
        i = 1
        for i, tx in enumerate(self._nicenames, start=1):
            Label(self, text=tx, justify="left", anchor="w", width=self.width
                  ).grid(row=i, column=0, sticky="nse")
        self.w = {k: v(self) for k, v in zip(self._refnames, self._wtypes)}

        for i, wn in enumerate(self._refnames, start=1):
            self.w[wn].grid(row=i, column=1)

        if newcb is not None:
            Button(self, text=f"Regisztrált {self._title} megnyitása..."
                   ).grid(row=i+1, column=0, columnspan=2, sticky="news")

    def _reset_widget(self, wname):
        self.w[wname].delete(0, "end")
        self.w[wname].focus_set()

    def check(self):
        for validor in self._validorz:
            if not validor(self):
                return
        self.results.incorporate({k: self.w[k].get() for k in ("name", "mnum", "akkn")})
        print(self.results.data)
        self.destroy()

    def lock(self):
        for w in self.w.values():
            w.configure(state="disabled", foreground="black")

    def unlock(self):
        for w in self.w.values():
            w.configure(state="active", foreground="black")


class MethodFrame(_Record):

    _title = "módszer"
    _refnames = "name", "mnum", "akkn", "staff"
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
        err = "Helytelen akkreditációs azonosító forma! Helyesen: pl. A/13"
        s = akkn.split("/")
        if "/" not in akkn or len(s) != 2 or not s[1].isdigit():
            _throw(err)
            self._reset_widget("akkn")
            return False
        return True

    _validorz = _valid_name, _valid_mnum, _valid_akkn

    def check(self):
        super().check()
        self.results["staff_id"] = self.dbifc.get_tasz(self.w["staff"].get())


class ParamFrame(_Record):

    _title = "paraméter"
    _refnames = "name", "dimension"
    _nicenames = "Megnevezés", "Mértékegység"
    _wtypes = _RecEntry, _RecEntry

    def _valid_name(self):
        assert self.upstream_ID is not None
        name = self.w["name"].get()
        if name:
            got = self.dbifc.query("SELECT id FROM Parameter WHERE method_id == ? AND name == ?",
                                   [self.upstream_ID, name])
            if got is None:
                return True
            _throw("{name} nevű paraméter már van ehhez a módszerhez!")
        else:
            _throw("Nevet kötelező megadni!")
        self.w["name"].focus_set()
        return False

    _validorz = (_valid_name,)


class CCFrame(_Record):

    _title = "kontroll diagram"
    _refnames = "startdate", "staff", "refmaterial", "comment", "refmean", "refstd", "uncertainty"
    _nicenames = "Felvéve (dátum)", "Felelős", "Anyagminta", "Megjegyzés", "Átlag", "Szórás", "Mérési bizonytalanság"
    _wtypes = _DateEntry, _StaffSelector, _RecEntry, _RecEntry, _RecEntry, _RecEntry, _RecEntry

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
        super().check()
        self.results["staff_id"] = self.dbifc.get_tasz(self.w["staff"].get())


if __name__ == '__main__':
    from tkinter import Tk
    from dbconnection import DBConnection
    conn = DBConnection()
    tk = Tk()
    nmkw = dict(master=tk, dbifc=conn, uID=1, bd=3, relief="raised")
    frames = [MethodFrame(**nmkw), ParamFrame(**nmkw), CCFrame(**nmkw)]
    for frame in frames:
        frame.pack()
    tk.mainloop()
