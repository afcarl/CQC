from tkinter import Tk, Menu, Frame
from tkinter import messagebox as tkmb

from ccmanager.chartholder import ChartHolder
from .propspanel import PropertiesPanel

from backend import globvars
from backend.plot_cc import cacheroot
from backend.dbconn import DBConnection


class CCManagerRoot(Frame):

    def __init__(self, master: Tk, **kw):
        super().__init__(master, **kw)
        globvars.logical_root = self

        self.master.title("CQC - Minőségirányítás - Kontroll diagram modul")
        self.dbifc = DBConnection(cacheroot+"TestDb.db", cacheroot+"meta.dat")

        self.pklpath = None
        self.active_panel = None
        self.active_toplevel = None

        self.menubar = Menu(self)
        self._build_ccmenu()
        self._build_viewmenu()
        self._build_pointsmenu()
        self.master.config(menu=self.menubar)

        self.mainframe = Frame(self)
        self.mainframe.pack(fill="both", expand=1)

        self.chartholder = ChartHolder(self.mainframe)
        self.chartholder.update_image()

        self.propspanel = PropertiesPanel(self.mainframe)
        self.activate_panel("properties")
        self.pack()

    def activate_panel(self, what):
        if self.active_panel is not None:
            self.active_panel.pack_forget()
        self.active_panel = {"control chart": self.chartholder,
                             "properties": self.propspanel}[what]
        self.active_panel.pack(fill="both", expand=1)

    def display(self, ccobj):
        self.chartholder = ChartHolder(self.mainframe)
        self.chartholder.set_ccobject(ccobj)

    def savecc_cmd(self):
        if not globvars.saved:
            globvars.saved = True
            self.pklpath = self.chartholder.ccobject.save()
        self.propspanel.lock()

    def newcc_cmd(self):
        if not globvars.saved:
            msg = ("A jelenlegi állapot nincs elmentve.",
                   "Szeretnéd menteni?")
            if tkmb.askyesno("Mentetlen adat!", "\n".join(msg)):
                self.savecc_cmd()

    def opencc_cmd(self):
        print("opencc_cmd called!")

    def deletecc_cmd(self):
        print("Called deletecc_cmd!")

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

    def _update_plot(self):
        self.chartholder.config(image=self.ccimg)
        self.saved = False
