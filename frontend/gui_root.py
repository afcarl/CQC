from tkinter import Tk, Menu, Label, PhotoImage


class Rootwin(Tk):

    def __init__(self):
        super().__init__()
        self.ccimg = None
        self.title("CQC - Vámlaboratóriumi minőségirányítás - Kontroll diagram modul")
        # self.geometry("1000x600")

        self.menubar = Menu(self)
        self._build_ccmenu()
        self._build_pointsmenu()
        self.config(menu=self.menubar)

        self.canvas = Label(self)
        self.canvas.pack(fill="both", expand=1)

        self._update_plot()

    def _build_ccmenu(self):
        fm = Menu(self.menubar)
        fm.add_command(label="Új...")
        fm.add_command(label="Megnyitás...")
        fm.add_command(label="Mentés")
        fm.add_command(label="Mentés másként...")
        fm.add_separator()
        fm.add_command(label="Tulajdonságok...")
        fm.add_separator()
        fm.add_command(label="Kilépés")
        self.menubar.add_cascade(label="Kontroll diagram", menu=fm)

    def _build_pointsmenu(self):
        pm = Menu(self.menubar)
        pm.add_command(label="Új pont felvétele")
        pm.add_command(label="Adatok szerkesztése")
        pm.add_separator()
        pm.add_command(label="Formatábla beforgarása")
        self.menubar.add_cascade(label="Pontok", menu=pm)

    def _update_plot(self):
        self.ccimg = PhotoImage(file="/home/csa/SciProjects/Project_CQC/cc_pic.png")
        self.canvas.config(image=self.ccimg)
