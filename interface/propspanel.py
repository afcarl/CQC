from collections import OrderedDict
from tkinter import Label, Frame, Button, Toplevel

from controlchart import Parameter

from interface.tablewidget import TkTable
from util.routine import replace_toplevel
from interface.reference_points import RefPointsTL

from util import globvars

pkw = dict(fill="both", expand=True)
pcfg = dict(bd=4, relief="raised")

hfields = OrderedDict(akkn="Módszer száma", methodname="Módszer",
                      methodowner="Módszer felelős", paramname="Paraméter",
                      dimension="Mértékegség", startdate="Felvéve",
                      refmaterial="Anyagminta",
                      ccowner="Diagramot felvette", comment="Megjegyzés")
sfields = OrderedDict(refmean="Átlag", refstd="Szórás",
                      uncertainty="Mérési bizonytalanság")


class PropertiesPanel(Frame):

    def __init__(self, master, ccparam=None, **kw):
        super().__init__(master, **kw)
        root = globvars.logical_root

        self.param = Parameter() if ccparam is None else ccparam  # type: Parameter
        self.reference_entry = None
        self.calc_button = None

        headervar = self.param.asvars("method") + self.param.asvars("cc")

        self.header = HeaderPart(self, fieldnames=hfields, tkvars=headervar, **pcfg)
        self.stats = StatsPart(self, fieldnames=sfields, tkvars=self.param.asvars("stat"), **pcfg)
        self.lock()

    @classmethod
    def astoplevel(cls, master, okcallback, ccparam=None, **kw):
        cctl = Toplevel(master)
        cctl.title("Kontroldiagram " +
                   ("létrehozás" if ccparam is None else "tulajdonságok"))
        ccpanel = cls(cctl, ccparam, **kw)
        ccpanel.pack(**pkw)

        Button(cctl, text="Kész", command=okcallback).pack(**pkw)
        Button(cctl, text="Mégsem", command=cctl.destroy).pack(**pkw)

        replace_toplevel(master=ccpanel, toplevel=cctl)

        return cctl

    def lock(self):
        self.header.lock()
        self.stats.lock()

    def unlock(self):
        self.header.unlock()
        self.stats.unlock()


class HeaderPart(Frame):

    def __init__(self, master, fieldnames, tkvars, **kw):
        super().__init__(master, **kw)
        labelconf = dict(justify="left", anchor="w", bd=1, relief="sunken", width=20)
        entryconf = dict(width=40)

        Label(self, text="Kontroll diagram adatok").pack()
        self.table = TkTable(self, fieldnames.values(), tkvars, labelconf, entryconf)
        self.table.pack(**pkw)
        Button(self, text="Adatok szerkesztése", command=self.unlock
               ).pack(**pkw)
        self.pack(**pkw)

    def lock(self):
        self.table.lock()

    def unlock(self):
        self.table.unlock()
        globvars.saved = False


class StatsPart(Frame):

    def __init__(self, master, fieldnames, tkvars, **kw):
        super().__init__(master, **kw)
        lbconf = dict(justify="left", anchor="w", bd=1, relief="sunken", width=20)
        entconf = dict(width=40)
        Label(self, text="Referencia statisztikák"
              ).pack(**pkw)
        cbconf = dict(text="Átlag és szórás számítása", command=self._launch_refentry,
                      state="disabled")

        self.calc_button = Button(self, cnf=cbconf)
        self.calc_button.pack(**pkw)

        self.table = TkTable(self, fieldnames.values(), tkvars, lbconf, entconf)
        self.table.pack(**pkw)

        Button(self, text="Statisztikák szerkesztése", command=self.unlock
               ).pack(**pkw)

        self.pack(**pkw)

    def _launch_refentry(self):
        self.reference_entry = RefPointsTL(self.master, 5)
        self.reference_entry.reposition()

    def lock(self):
        self.table.lock()
        self.calc_button.configure(state="disabled")

    def unlock(self):
        self.table.unlock()
        self.calc_button.configure(state="normal")
        globvars.saved = False
