from tkinter import Label, Frame, Button
from statistics import mean, stdev

from controlchart import ControlChart
from interface.tablewidget import TkTable
from interface.measurements import NewMeasurements
from util import globvars

pkw = dict(fill="both", expand=True)
pcfg = dict(bd=4, relief="raised")


class PropertiesPanel(Frame):

    def __init__(self, master, ccobj, **kw):
        super().__init__(master, **kw)

        self.ccobj = ccobj  # type: ControlChart

        self.calc_button = None

        self.header = HeaderPart(self, param=ccobj, **pcfg)
        self.stats = StatsPart(self, param=ccobj, **pcfg)
        self.lock()

    def lock(self):
        self.header.lock()
        self.stats.lock()

    def unlock(self):
        self.header.unlock()
        self.stats.unlock()


class HeaderPart(Frame):

    def __init__(self, master, param: ControlChart, **kw):
        super().__init__(master, **kw)
        md, pd, ccd = param.mrec, param.prec, param.ccrec
        recvars = (
            md.akkn, md.name, md.staff_id, pd.name, pd.dimension,
            ccd.startdate, ccd.refmaterial, ccd.staff_id, ccd.comment
        )
        fieldnames = (
            "Módszer száma", "Módszer", "Módszer felelős", "Paraméter",
            "Mértékegség", "Felvéve", "Anyagminta", "Diagramot felvette", "Megjegyzés"
        )
        labelconf = dict(justify="left", anchor="w", bd=1, relief="sunken", width=20)
        entryconf = dict(width=40)

        Label(self, text="Kontroll diagram adatok").pack()
        self.table = TkTable(self, fieldnames, recvars, labelconf, entryconf)
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

    def __init__(self, master, param: ControlChart, **kw):
        super().__init__(master, **kw)
        ccd = param.ccrec
        tkvars = (ccd.refmean, ccd.refstd, ccd.uncertainty)
        fieldnames = ("Átlag", "Szórás", "Mérési bizonytalanság")

        lbconf = dict(justify="left", anchor="w", bd=1, relief="sunken", width=20)
        entconf = dict(width=40)

        Label(self, text="Referencia statisztikák").pack(**pkw)

        self.calc_button = Button(self, text="Átlag és szórás számítása",
                                  command=self._launch_refentry, state="disabled")
        self.calc_button.pack(**pkw)

        self.table = TkTable(self, fieldnames, tkvars, lbconf, entconf)
        self.table.pack(**pkw)

        Button(self, text="Statisztikák szerkesztése", command=self.unlock).pack(**pkw)

        self.param = param
        self.pack(**pkw)

    def _launch_refentry(self):
        rent = NewMeasurements(self.master, self.param.refmeas, rown=5, title="Referencia pontok bevitele")
        self.wait_window(rent)
        if len(rent.results) < 3:
            return
        points = [p for p, d, c in rent.results]
        self.param.ccrec["refmean"] = mean(points)
        self.param.ccrec["refstd"] = stdev(points)

    def lock(self):
        self.table.lock()
        self.calc_button.configure(state="disabled")

    def unlock(self):
        self.table.unlock()
        self.calc_button.configure(state="normal")
        globvars.saved = False
