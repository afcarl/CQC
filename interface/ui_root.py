from tkinter import Tk, Menu, Frame, Button, messagebox as tkmb

from dbconnection import DBConnection
from controlchart import ControlChart

from .chartholder import ChartHolder
from .propspanel import PropertiesPanel
from .selection_wizard import SelectionWizard
from .measurements import NewMeasurements, EditMeasurements

from util import globvars

pkw = dict(fill="both", expand=True)


class CCManagerRoot(Frame):

    def __init__(self, master: Tk, **kw):
        super().__init__(master, **kw)
        globvars.logical_root = self

        self.master.title("CQC - Kontroll diagram modul")

        self.dbifc = DBConnection()

        self.pklpath = None
        self.active_panel = None
        self.active_toplevel = None
        self.ccobject = ControlChart()

        self.menubar = Menu(self)
        self._build_filemenu()
        self._build_editmenu()
        self._build_viewmenu()
        self.master.config(menu=self.menubar)

        self.mainframe = Frame(self)
        self.mainframe.pack(**pkw)

        self.chartholder = ChartHolder(self.mainframe)
        self.chartholder.update_image()

        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)
        self.activate_panel("control chart")
        bframe = Frame(self)
        bs = [Button(bframe, text="Kész", command=self.savecc_cmd),
              Button(bframe, text="Törlés", command=self.deletecc_cmd)]
        for b in bs:
            b.pack(side="left", **pkw)
        self.switchbutton = Button(
            bframe, text="Nézetváltás", command=self.switch_panel
        )
        self.switchbutton.pack(side="left", **pkw)
        bframe.pack(**pkw)

        self.pack(**pkw)

    def switch_panel(self):
        self.activate_panel(
            "control chart" if isinstance(self.active_panel, PropertiesPanel) else "properties"
        )

    def activate_panel(self, what):
        if self.active_panel is not None:
            self.active_panel.pack_forget()
        self.active_panel = {"control chart": self.chartholder,
                             "properties": self.propspanel}[what]
        self.active_panel.pack(**pkw)

    def savecc_cmd(self):
        self.propspanel.lock()
        if globvars.saved or self.ccobject is None:
            return
        globvars.saved = True
        ccobj = self.ccobject
        self.dbifc.update_cc(ccobj)

    def newcc_cmd(self):
        if not globvars.saved:
            msg = ("A jelenlegi állapot nincs elmentve.",
                   "Szeretnéd menteni?")
            if tkmb.askyesno("Mentetlen adat!", "\n".join(msg)):
                self.savecc_cmd()
        self.ccobject = ControlChart()
        self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)
        self.propspanel.unlock()
        self.activate_panel("properties")
        self.chartholder.update_image(None)
        globvars.saved = False

    def opencc_cmd(self):
        wiz = SelectionWizard(self)
        self.wait_window(wiz)
        if wiz.selection["cc"] is None:
            return
        self.ccobject = ControlChart.from_database(
            dbifc=self.dbifc, ccID=wiz.selection["cc"],
        )
        self.chartholder.update_image(self.ccobject)
        self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self.mainframe, self.ccobject)
        self.activate_panel("properties")

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

    def _build_filemenu(self):
        fm = Menu(self.menubar, tearoff=0)
        fm.add_command(label="Új...", command=self.newcc_cmd)
        fm.add_command(label="Megnyitás...", command=self.opencc_cmd)
        fm.add_command(label="Mentés", command=self.savecc_cmd)
        fm.add_command(label="Mentés másként...")
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...")
        fm.add_separator()
        fm.add_command(label="Biztonsági mentések...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.menubar.add_cascade(label="Fájl", menu=fm)

    def _build_viewmenu(self):
        fm = Menu(self.menubar, tearoff=0)
        fm.add_command(label="Diagram",
                       command=lambda: self.activate_panel("control chart"))
        fm.add_command(label="Tulajdonságok",
                       command=lambda: self.activate_panel("properties"))
        self.menubar.add_cascade(label="Nézet", menu=fm)

    def _build_editmenu(self):
        pm = Menu(self.menubar, tearoff=0)
        pm.add_command(label="Új pont felvétele", command=self.newpoints_cmd)
        pm.add_command(label="Adatok szerkesztése", command=self.editpoints_cmd)
        pm.add_separator()
        pm.add_command(label="Formatábla beforgarása")
        pm.add_separator()
        pm.add_command(label="Visszavonás")
        self.menubar.add_cascade(label="Szerkesztés", menu=pm)
