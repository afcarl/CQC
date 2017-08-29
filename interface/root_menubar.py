from tkinter import Menu

from util import globvars


class RootMenu(Menu):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._build_filemenu()
        self._build_editmenu()
        self._build_viewmenu()

    def _build_filemenu(self):
        lr = globvars.logical_root
        fm = Menu(self, tearoff=0)
        fm.add_command(label="Új...", command=lr.newcc_cmd)
        fm.add_command(label="Megnyitás...", command=lr.opencc_cmd)
        fm.add_command(label="Mentés", command=lr.savecc_cmd)
        fm.add_command(label="Mentés másként...")
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...")
        fm.add_separator()
        fm.add_command(label="Biztonsági mentések...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.add_cascade(label="Fájl", menu=fm)

    def _build_viewmenu(self):
        lr = globvars.logical_root
        fm = Menu(self, tearoff=0)
        fm.add_command(label="Diagram",
                       command=lambda: lr.activate("control chart"))
        fm.add_command(label="Tulajdonságok",
                       command=lambda: lr.activate("properties"))
        self.add_cascade(label="Nézet", menu=fm)

    def _build_editmenu(self):
        lr = globvars.logical_root
        pm = Menu(self, tearoff=0)
        pm.add_command(label="Új pont felvétele", command=lr.newpoints_cmd)
        pm.add_command(label="Adatok szerkesztése", command=lr.editpoints_cmd)
        pm.add_separator()
        pm.add_command(label="Formatábla beforgarása")
        pm.add_separator()
        pm.add_command(label="Visszavonás")
        self.add_cascade(label="Szerkesztés", menu=pm)
