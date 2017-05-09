from tkinter import Toplevel, Label, Entry, Frame, Button, StringVar

from .gui_widgets import RefPointsTL
from ..backend.util import floatify


class PropertiesCC(Toplevel):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.title("Új kontroll diagram felvétele")
        self.resizable(False, False)
        self.fields = ("Módszer", "Anyagminta", "Mért paraméter neve", "Mértékegység")
        self.entries = {}
        self.header_entry_frame = Frame(self)  # entry frame
        self.header_entry_frame.pack()
        self._add_entries_and_labels()
        self.readybutton = None
        self.reference_entry = None
        self.reference_stats = [StringVar() for _ in range(3)]
        self._add_buttons()

    def reposition(self):
        x, y = self.master.winfo_x(), self.master.winfo_y()
        self.update()
        w, h = self.winfo_width(), self.winfo_height()
        dx = x + w//2
        dy = y + h//2
        self.geometry(f"{w}x{h}+{dx}+{dy}")

    def _add_entries_and_labels(self):
        labelconf = {"justify": "left", "anchor": "w"}
        entryconf = {"width": 40}
        for n, field in enumerate(self.fields):
            Label(self.header_entry_frame, text=field, cnf=labelconf
                  ).grid(row=n, column=0, sticky="news")
            e = Entry(self.header_entry_frame, cnf=entryconf)
            e.grid(row=n, column=1, sticky="news")
            self.entries[field] = e

    def _add_buttons(self):
        tf = Frame(self, bd=3, relief="raised")
        Label(tf, text="Referencia statisztikák megadása (átlag, szórás, stb.)"
              ).grid(row=0, column=0, columnspan=2, sticky="news")
        Button(tf, text="Átlag és szórás számítása", command=self._launch_refentry
               ).grid(row=1, column=0, columnspan=2)
        for rown, (tx, var) in enumerate(zip(
                ("Átlag", "Szórás", "Mérési bizonytalanság"),
                self.reference_stats), start=2):

            Label(tf, text=tx, justify="left", anchor="w", bd=1, relief="sunken"
                  ).grid(row=rown, column=0, sticky="news")
            Entry(tf, textvar=var, width=40
                  ).grid(row=rown, column=1, sticky="news")
        tf.pack(fill="both", expand=1)
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)

        self.readybutton = Button(self, text="Kész", command=self.setvars)
        self.readybutton.pack(fill="both")
        Button(self, text="Mégsem", command=self.destroy
               ).pack(fill="both")

    def _launch_refentry(self):
        self.reference_entry = RefPointsTL(self, 5)
        self.reference_entry.reposition()

    def get_params(self):
        return [self.entries[f].get() for f in self.fields]

    def pull_data(self):
        header = [self.entries[fld].get() for fld in self.fields]
        stats = [floatify(var.get()) for var in self.reference_stats]
        return header + stats

    def setvars(self):
        # TODO: set CC vars and exit
        self.master.instantiate_cc(self.pull_data())
        self.destroy()
