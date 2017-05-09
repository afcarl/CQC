from tkinter import Tk, Menu, Label, PhotoImage, TclError, Frame

from .abstractions import CCHandlerMixin
from .gui_cchart_builder import PropertiesCC

from ..backend.routines import instantiate_cc
from ..backend.plot_cc import cacheroot
from ..backend.dbconn import DBConnection


class Rootwin(Tk, CCHandlerMixin):

    def __init__(self):
        super().__init__()
        self.title("CQC - Vámlaboratóriumi minőségirányítás - Kontroll diagram modul")
        # self.geometry("1000x600")
        self.ccimg = PhotoImage(file=cacheroot+"emptycc.png")
        self.dbifc = DBConnection(cacheroot+"TestDb.db", cacheroot+"meta.dat")

        self.saved = True
        self.active_tl = None

        self.menubar = Menu(self)
        self._build_ccmenu()
        self._build_pointsmenu()
        self.config(menu=self.menubar)

        self.dataframe = Frame(self)
        self.dataframe.pack(side="right", fill="both")
        self.canvas = Label(self)
        self.canvas.pack(side="right", fill="both", expand=1)

        self._update_plot()

    def activate_toplevel(self, what):
        try:
            self.active_tl.destroy()
        except AttributeError or TclError:
            pass
        self.active_tl = {"CreateCC": PropertiesCC}[what](self)
        self.active_tl.reposition()
        self.active_tl.grab_set()

    def set_cc(self, name, data):
        cc = instantiate_cc(data)
        self.ccobjects[cc.ID] = cc
        self.ccimg = PhotoImage(file=self.ccobject.imgpath)
        self._update_plot()

    def _build_ccmenu(self):
        fm = Menu(self.menubar, tearoff=0)
        fm.add_command(label="Új...", command=lambda: self.activate_toplevel("CreateCC"))
        fm.add_command(label="Megnyitás...")
        fm.add_command(label="Mentés")
        fm.add_command(label="Mentés másként...")
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.menubar.add_cascade(label="Kontroll diagram", menu=fm)

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

    def _save_state(self):
        if self.saved:
            return
        self.ccobject