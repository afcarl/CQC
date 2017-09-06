from tkinter import Tk, Button, messagebox as tkmb

from dbconnection import DBConnection
from controlchart import ControlChart
from interface.propspanel import PropertiesPanel
from util import pkw

from .root_menubar import RootMenu
from .chartholder import ChartHolder
from .selection_wizard import SelectionWizard
from .measurements import NewMeasurements, EditMeasurements


class CCManagerRoot(Tk):

    dbifc = DBConnection()

    def __init__(self, **kw):
        super().__init__(**kw)

        self.title("CQC - Kontroll diagram modul")

        self.active_panel = None
        self.active_toplevel = None
        self.ccobject = ControlChart()

        self.menubar = RootMenu(self)
        self.config(menu=self.menubar)
        self.menubar.lock()

        self.chartholder = ChartHolder(self)
        self.chartholder.update_image(None)
        self.chartholder.pack(**pkw)
        self.propspanel = None
        self.properties_button = Button(
            self, text="Tulajdonságok megjelenítése", state="disabled",
            command=lambda: self.launch_propspanel(stage=None)
        )
        self.properties_button.pack(**pkw)

    def launch_propspanel(self, stage=None):
        if self.propspanel is not None:
            self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self, self.ccobject, self.dbifc, stage)

    def savecc_cmd(self):
        if self.ccobject.unsaved is None:
            print("UNSAVED IS NONE! NOT SAVING!")
            return
        if self.ccobject.ccrec["id"] is None:
            self.dbifc.push_object(self.ccobject)
        else:
            self.dbifc.update_cc(self.ccobject)

    def newcc_cmd(self):
        if self.ccobject.unsaved:
            msg = ("A jelenlegi állapot nincs elmentve.",
                   "Szeretnéd menteni?")
            if tkmb.askyesno("Mentetlen adat!", "\n".join(msg)):
                self.savecc_cmd()
        wiz = self._build_stage()
        if wiz is None:
            return
        self.launch_propspanel(wiz.stage)
        self.wait_window(self.propspanel)
        self.ccobject.set_upstream_ids()
        self.propspanel = None
        IDs = self.dbifc.push_object(self.ccobject)
        rex = self.ccobject.rec
        for rectype, ID in IDs.items():
            if ID is None:
                assert rex[rectype]["id"] is not None, f"@ {rectype} (ID: {ID})"
            rex[rectype]["id"] = ID
            assert rex[rectype]["id"] is None, f"@ {rectype} (ID: {ID})\nIDs: {IDs}\nrecdata: {rex[rectype].data}"
        self.chartholder.update_image(self.ccobject)
        self.menubar.unlock()
        self.properties_button.configure(state="active")

    def opencc_cmd(self):
        wiz = SelectionWizard(self, creation_mode=False, skipempties=True)
        self.wait_window(wiz)
        if wiz.stage is None:
            return
        cc = ControlChart.from_database(
            dbifc=self.dbifc, ccID=wiz.selection["cc"],
        )
        self.ccobject = cc
        self.chartholder.update_image(self.ccobject)
        self.menubar.unlock()
        self.properties_button.configure(state="active")

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
        self.menubar.lock()

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

    def _build_stage(self):
        wiz = SelectionWizard(self, creation_mode=True, skipempties=False)
        self.wait_window(wiz)
        if wiz.stage is None:
            return
        self.ccobject = ControlChart.build_stage(wiz.selection, wiz.stage, self.dbifc)
        return wiz
