from tkinter import Menu


class RootMenu(Menu):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._build_filemenu()
        self._build_editmenu()
        self._build_viewmenu()

    def _build_filemenu(self):
        m = self.master
        fm = Menu(self, tearoff=0)
        fm.add_command(label="Új...", command=m.newcc_cmd)
        fm.add_command(label="Megnyitás...", command=m.opencc_cmd)
        fm.add_command(label="Mentés", command=m.savecc_cmd)
        fm.add_command(label="Mentés másként...")
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...")
        fm.add_separator()
        fm.add_command(label="Biztonsági mentések...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.add_cascade(label="Fájl", menu=fm)

    def _build_viewmenu(self):
        m = self.master
        fm = Menu(self, tearoff=0)
        fm.add_command(label="Diagram",
                       command=lambda: m.mainframe.activate("ControlChart"))
        fm.add_command(label="Tulajdonságok",
                       command=lambda: m.mainframe.activate("PropertiesPanel"))
        self.add_cascade(label="Nézet", menu=fm)

    def _build_editmenu(self):
        m = self.master
        pm = Menu(self, tearoff=0)
        pm.add_command(label="Új pont felvétele", command=m.newpoints_cmd)
        pm.add_command(label="Adatok szerkesztése", command=m.editpoints_cmd)
        pm.add_separator()
        pm.add_command(label="Formatábla beforgarása")
        pm.add_separator()
        pm.add_command(label="Visszavonás")
        self.add_cascade(label="Szerkesztés", menu=pm)
