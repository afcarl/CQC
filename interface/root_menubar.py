from tkinter import Menu


class RootMenu(Menu):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.filemenu = None
        self._me_lockables = ["Mentés", "Tulajdonságok..."]
        self._build_filemenu()
        self._build_editmenu()

    def _build_filemenu(self):
        m = self.master
        fm = Menu(self, tearoff=0)
        fm.add_command(label="Új...", command=m.newcc_cmd)
        fm.add_command(label="Megnyitás...", command=m.opencc_cmd)
        fm.add_command(label="Mentés", command=m.savecc_cmd)
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...", command=m.launch_propspanel)
        fm.add_separator()
        fm.add_command(label="Biztonsági mentések...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.add_cascade(label="Fájl", menu=fm)
        self.filemenu = fm

    def _build_editmenu(self):
        m = self.master
        em = Menu(self, tearoff=0)
        em.add_command(label="Új pont felvétele", command=m.newpoints_cmd)
        em.add_command(label="Adatok szerkesztése", command=m.editpoints_cmd)
        em.add_separator()
        em.add_command(label="Formatábla beforgarása")
        em.add_separator()
        em.add_command(label="Visszavonás")
        self.add_cascade(label="Szerkesztés", menu=em)

    def _set_states(self, state):
        for me in self._me_lockables:
            self.filemenu.entryconfig(me, state=state)
        self.entryconfig("Szerkesztés", state=state)

    def lock(self):
        self._set_states("disabled")

    def unlock(self):
        self._set_states("normal")
