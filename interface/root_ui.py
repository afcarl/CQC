from tkinter import Tk, Frame, Button, messagebox as tkmb

from dbconnection import DBConnection
from controlchart import ControlChart

from .root_menubar import RootMenu
from .root_mainframe import RootMainFrame
from .chartholder import ChartHolder
from .propspanel import PropertiesPanel
from .selection_wizard import SelectionWizard
from .measurements import NewMeasurements, EditMeasurements

from util import globvars

pkw = dict(fill="both", expand=True)


class CCManagerRoot(Frame):

    dbifc = DBConnection()

    def __init__(self, master: Tk, **kw):
        super().__init__(master, **kw)
        globvars.logical_root = self

        self.master.title("CQC - Kontroll diagram modul")

        self.active_panel = None
        self.active_toplevel = None
        self.ccobject = ControlChart()

        self.master.config(menu=(RootMenu(self)))

        self.mainframe = RootMainFrame(self)
        self.mainframe.pack(**pkw)

        self.chartholder = ChartHolder(self.mainframe)
        self.chartholder.update_image(None)
        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)

        self.mainframe.activate("ChartHolder")
        Button(self, text="Nézetváltás", command=self.mainframe.switch).pack(**pkw)
        self.pack(**pkw)

    def savecc_cmd(self):
        self.propspanel.lock()
        if globvars.saved or self.ccobject is None:
            return
        globvars.saved = True
        self.dbifc.update_cc(self.ccobject)

    def newcc_cmd(self):
        if not globvars.saved:
            msg = ("A jelenlegi állapot nincs elmentve.",
                   "Szeretnéd menteni?")
            if tkmb.askyesno("Mentetlen adat!", "\n".join(msg)):
                self.savecc_cmd()
        wiz = SelectionWizard(self, skipempties=False)
        self.wait_window(wiz)
        if wiz.stage is None:
            return
        self.ccobject = ControlChart.build_stage(wiz.selection, wiz.stage, self.dbifc)
        self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)
        self.propspanel.unlock(until=wiz.stage)
        self.mainframe.activate("PropertiesPanel")
        self.chartholder.update_image(self.ccobject)
        globvars.saved = False
        print("SW terminated @ stage:", wiz.stage)

    def opencc_cmd(self):
        wiz = SelectionWizard(self, skipempties=True)
        self.wait_window(wiz)
        if wiz.stage is None:
            return
        self.ccobject = ControlChart.from_database(
            dbifc=self.dbifc, ccID=wiz.selection["cc"],
        )
        self.chartholder.update_image(self.ccobject)
        self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)
        self.mainframe.activate("ChartHolder")

    def deletecc_cmd(self):
        msg = "Valóban törölni szeretnéd a kontroll diagramot?"
        if not tkmb.askyesno("Törlés megerősítése", msg):
            return
        if self.ccobject.ID is not None:
            self.dbifc.delete_cc(self.ccobject.ID)
            path = self.ccobject.pkldump()
            print("Backed up ControlChart object to", path)
        self.ccobject = ControlChart()
        self.chartholder.update_image(None)
        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)

    def newpoints_cmd(self):
        mtl = NewMeasurements(
            self, self.ccobject.meas, rown=3, title="Pontok bevitele"
        )
        self.wait_window(mtl)
        print("NEW POINTS:")
        print("VALUE\tDATE\tCOMMENT")
        print("\n".join("\t".join(map(str, line)) for line in mtl.results))

    def editpoints_cmd(self):
        mtl = EditMeasurements(
            self, self.ccobject.meas, rown=10, title="Pontok szerkesztése"
        )
        self.wait_window(mtl)
