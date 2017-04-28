from tkinter import Tk, Toplevel, Label, Entry, Frame, Button


class CreateCC(Toplevel):

    def __init__(self, master: Tk, **kw):
        super().__init__(master, **kw)
        self.title("Új kontroll diagram felvétele")
        self.fields = ("Módszer", "Anyagminta", "Mért paraméter neve", "Mértékegység")
        self.entries = {}
        self.efr = Frame(self)  # entry frame
        self.efr.pack()
        self._add_entries_and_labels()
        self._add_buttons()

    def replace(self):
        x, y = self.master.winfo_x(), self.master.winfo_y()
        self.update()
        w, h = self.winfo_width(), self.winfo_height()
        dx = x + w//2
        dy = y + h//2
        self.geometry(f"{w}x{h}+{dx}+{dy}")

    def _add_entries_and_labels(self):
        labelconf = {"width": 20, "justify": "left", "anchor": "nw"}
        entryconf = {"width": 40}
        for n, field in enumerate(self.fields):
            Label(self.efr, text=field, cnf=labelconf).grid(row=n, column=0)
            e = Entry(self.efr, cnf=entryconf)
            e.grid(row=n, column=1)
            self.entries[field] = e

    def _add_buttons(self):
        bw = 7
        Button(self, text="Kész", width=bw, command=self.setvars
               ).pack(fill="both")
        Button(self, text="Mégsem", width=bw, command=self.closeme
               ).pack(fill="both")

    def get_params(self):
        return [self.entries[f].get() for f in self.fields]

    def closeme(self):
        self.destroy()

    def setvars(self):
        # TODO: set CC vars and exit
        self.destroy()

if __name__ == '__main__':
    root = CreateCC(None)
    root.mainloop()
