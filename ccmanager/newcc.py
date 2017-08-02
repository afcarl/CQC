from tkinter import Frame, Label, Entry, Listbox


class BuilderRoot(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        Label(self, "Kontroll diagram létrehozása").pack(fill="both", expand=True)
        self.lb = Listbox(self)
        self.lb.pack()


