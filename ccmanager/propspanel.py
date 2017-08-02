from tkinter import Label, Frame, Button, Toplevel

from backend import globvars

from .abstraction import TkTable, replace_toplevel
from .reference_points import RefPointsTL
from backend.parameter import CCParams


class PropertiesPanel(Frame):

    def __init__(self, master, ccparams=None, **kw):
        super().__init__(master, **kw)
        root = globvars.logical_root

        self.data = CCParams() if ccparams is None else ccparams
        self.reference_entry = None
        self.calc_button = None

        hfields = ("Módszer", "Anyagminta", "Mért paraméter neve",
                   "Mértékegység", "Revízió", "Megjegyzés")
        sfields = ("Átlag", "Szórás", "Mérési bizonytalanság")

        self.header = HeaderPart(self, fieldnames=hfields, tkvars=self.data.headervars())
        self.stats = StatsPart(self, fieldnames=sfields, tkvars=self.data.statvars())
        self.header.pack()
        self.stats.pack()
        self.lock()

        bframe = Frame(self)
        bs = [Button(bframe, text="Kész", width=8, command=root.savecc_cmd),
              Button(bframe, text="Törlés", width=8, command=root.deletecc_cmd),
              Button(bframe, text="Diagram", width=8,
                     command=lambda: root.activate_panel("control chart"))]
        for b in bs:
            b.pack(side="left", fill="both", expand=True)
        bframe.pack(fill="both", expand=True)

    @classmethod
    def astoplevel(cls, master, okcallback, ccparam=None, **kw):
        cctl = Toplevel(master)
        cctl.title("Kontroldiagram " +
                   ("létrehozás" if ccparam is None else "tulajdonságok"))
        ccpanel = cls(cctl, ccparam, **kw)
        ccpanel.pack()

        Button(cctl, text="Kész", command=okcallback).pack(fill="both")
        Button(cctl, text="Mégsem", command=cctl.destroy).pack(fill="both")

        replace_toplevel(master=ccpanel, toplevel=cctl)

        return cctl

    def lock(self):
        self.header.lock()
        self.stats.lock()

    def unlock(self):
        self.header.unlock()
        self.stats.unlock()
        self.calc_button.configure(state="normal")

    def pull_data(self):
        return self.data


class HeaderPart(Frame):

    def __init__(self, master, fieldnames, tkvars, **kw):
        super().__init__(master, **kw)
        labelconf = dict(justify="left", anchor="w", bd=1, relief="sunken", width=20)
        entryconf = dict(width=40)

        hframe = Frame(self, bd=4, relief="raised")
        Label(hframe, text="Kontroll diagram adatok").pack()
        self.table = TkTable(hframe, fieldnames, tkvars, labelconf, entryconf)
        self.table.pack()
        self.table.grid_rowconfigure(0, weight=1)
        self.table.grid_columnconfigure(0, weight=1)
        Button(hframe, text="Adatok szerkesztése", command=self.table.unlock
               ).pack(expand=True, fill="both")
        hframe.pack()

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
        statframe = Frame(self, bd=4, relief="raised")
        Label(statframe, text="Referencia statisztikák"
              ).pack(fill="both", expand=1)
        cbconf = dict(text="Átlag és szórás számítása", command=self._launch_refentry,
                      state="disabled")

        self.calc_button = Button(statframe, cnf=cbconf)
        self.calc_button.pack(expand=True, fill="both")

        self.table = TkTable(statframe, fieldnames, tkvars, lbconf, entconf)
        self.table.pack(fill="both", expand=1)
        self.table.grid_rowconfigure(0, weight=1)
        self.table.grid_columnconfigure(0, weight=1)

        Button(statframe, text="Statisztikák szerkesztése", command=self.unlock
               ).pack(fill="both", expand=1)

        statframe.pack(fill="both", expand=1)
        statframe.grid_rowconfigure(0, weight=1)
        statframe.grid_columnconfigure(0, weight=1)

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
