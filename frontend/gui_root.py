from tkinter import Tk, Menu, Frame
from tkinter import messagebox as tkmb

from .gui_widgets import ChartHolder
from .gui_propspanel import PropertiesPanel

from ..backend.plot_cc import cacheroot
from ..backend.dbconn import DBConnection


class Rootwin(Tk):

    def __init__(self):
        super().__init__()
        self.title("CQC - Minőségirányítás - Kontroll diagram modul")
        self.dbifc = DBConnection(cacheroot+"TestDb.db", cacheroot+"meta.dat")

        self.saved = True
        self.pklpath = None
        self.active_panel = None
        self.active_toplevel = None

        self.menubar = Menu(self)
        self._build_ccmenu()
        self._build_viewmenu()
        self._build_pointsmenu()
        self.config(menu=self.menubar)

        self.mainframe = Frame(self)
        self.mainframe.pack(fill="both", expand=1)

        self.canvas = ChartHolder(self.mainframe)
        self.canvas.update_image()

        self.propspanel = PropertiesPanel(self.mainframe)
        self.activate_panel("properties")

        # self.resizable(False, False)

    def _select_component(self, cname):
        components = {
            "control chart": self.canvas,
            "properties": self.propspanel,
        }
        return components[cname]

    def activate_panel(self, what):
        if self.active_panel is not None:
            self.active_panel.pack_forget()
        self.active_panel = self._select_component(what)
        self.active_panel.pack(fill="both", expand=1)

    def display(self, ccobj):
        self.canvas = ChartHolder(self.mainframe)
        self.canvas.set_ccobject(ccobj)

    def _savecc_cmd(self):
        self.pklpath = self.canvas.ccobject.save()
        self.saved = True

    def _newcc_cmd(self):
        if not self.saved:
            msg = ("A jelenlegi állapot nincs elmentve.",
                   "Szeretnéd menteni?")
            if tkmb.askyesno("Mentetlen adat!", "\n".join(msg)):
                self._savecc_cmd()

    def _build_ccmenu(self):
        fm = Menu(self.menubar, tearoff=0)
        fm.add_command(label="Új...", command=lambda: self.newcc_cmd("CreateCC"))
        fm.add_command(label="Megnyitás...")
        fm.add_command(label="Mentés")
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

    def _update_plot(self):
        self.canvas.config(image=self.ccimg)
        self.saved = False
