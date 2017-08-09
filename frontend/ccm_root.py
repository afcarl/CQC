from tkinter import Tk, Menu, Frame, messagebox as tkmb

from backend import globvars
from backend.cchart import ControlChart
from backend.parameter import AllParameter

from frontend.chartholder import ChartHolder
from frontend.selection_wizard import SelectionWizard
from frontend.propspanel import PropertiesPanel

from dbconnection.interface import DBConnection


class CCManagerRoot(Frame):

    def __init__(self, master: Tk, **kw):
        super().__init__(master, **kw)
        globvars.logical_root = self

        self.master.title("CQC - Minőségirányítás - Kontroll diagram modul")

        self.dbifc = DBConnection()

        self.pklpath = None
        self.active_panel = None
        self.active_toplevel = None

        self.menubar = Menu(self)
        self._build_ccmenu()
        self._build_viewmenu()
        self._build_pointsmenu()
        self.master.config(menu=self.menubar)

        self.mainframe = Frame(self)
        self.mainframe.pack(fill="both", expand=True)

        self.chartholder = ChartHolder(self.mainframe)
        self.chartholder.update_image()

        self.propspanel = PropertiesPanel(self.mainframe)
        self.activate_panel("control chart")
        self.pack(fill="both", expand=True)

    def activate_panel(self, what):
        if self.active_panel is not None:
            self.active_panel.pack_forget()
        self.active_panel = {"control chart": self.chartholder,
                             "properties": self.propspanel}[what]
        self.active_panel.pack(fill="both", expand=True)

    def savecc_cmd(self):
        if not globvars.saved:
            globvars.saved = True
            if self.chartholder.ccobject is None:
                points = None  # TODO: work more on the points part!
                ID, ccparam = self.propspanel.pull_data()
                self.chartholder.set_ccobject(ControlChart(ccparam, ID, points))
            self.chartholder.ccobject.save()
        self.propspanel.lock()

    def newcc_cmd(self):
        if not globvars.saved:
            msg = ("A jelenlegi állapot nincs elmentve.",
                   "Szeretnéd menteni?")
            if tkmb.askyesno("Mentetlen adat!", "\n".join(msg)):
                self.savecc_cmd()
        self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self.mainframe)
        self.propspanel.unlock()
        self.activate_panel("properties")
        self.chartholder.set_ccobject(None)
        globvars.saved = False

    def opencc_cmd(self):
        wiz = SelectionWizard(self)
        self.wait_window(wiz)
        if wiz.selection["cc"] is None:
            return
        ccID = wiz.selection["cc"]
        ccdata, points = self.dbifc.ccobj_args(ccID)
        ccparam = Parameter.from_values(ccdata)
        self.chartholder.set_ccobject(
            ControlChart(ID=ccID, ccparam=ccparam, points=points)
        )
        self.propspanel.destroy()
        self.propspanel = PropertiesPanel(self.mainframe, ccparam)
        self.activate_panel("properties")

    def deletecc_cmd(self):
        msg = "Valóban törölni szeretnéd a kontroll diagramot?"
        if not tkmb.askyesno("Törlés megerősítése", msg):
            return
        ccobject = self.chartholder.ccobject
        self.chartholder.set_ccobject(None)
        self.propspanel = PropertiesPanel(self.mainframe)
        if ccobject.ID is not None:
            self.dbifc.delete_cc(ccobject.ID)
            path = ccobject.backup()
            print("Backed up ControlChart object to", path)

    def _build_ccmenu(self):
        fm = Menu(self.menubar, tearoff=0)
        fm.add_command(label="Új...", command=self.newcc_cmd)
        fm.add_command(label="Megnyitás...", command=self.opencc_cmd)
        fm.add_command(label="Mentés", command=self.savecc_cmd)
        fm.add_command(label="Mentés másként...")
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.menubar.add_cascade(label="Kontroll diagram", menu=fm)

    def _build_viewmenu(self):
        fm = Menu(self.menubar, tearoff=0)
        fm.add_command(label="Diagram",
                       command=lambda: self.activate_panel("control chart"))
        fm.add_command(label="Tulajdonságok",
                       command=lambda: self.activate_panel("properties"))
        self.menubar.add_cascade(label="Nézet", menu=fm)

    def _build_pointsmenu(self):
        pm = Menu(self.menubar, tearoff=0)
        pm.add_command(label="Új pont felvétele")
        pm.add_command(label="Adatok szerkesztése")
        pm.add_separator()
        pm.add_command(label="Formatábla beforgarása")
        self.menubar.add_cascade(label="Pontok", menu=pm)
