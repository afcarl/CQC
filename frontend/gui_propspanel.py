from tkinter import Label, Entry, Frame, Button, Toplevel

from .gui_widgets import RefPointsTL
from ..backend.util import CCParams


class PropertiesPanel(Frame):

    def __init__(self, master, ccparams=None, **frame_kw):

        super().__init__(master, **frame_kw)

        self.fields = (
            "Módszer", "Anyagminta", "Mért paraméter neve",
            "Mértékegység", "Revízió", "Megjegyzés"
        )
        self.entries = {}
        self.data = CCParams() if ccparams is None else ccparams
        self.readybutton = None
        self.reference_entry = None

        self._build_header_part()
        self._add_sep()
        self._build_stats_part()

    @classmethod
    def astoplevel(cls, master, okcallback, ccparam=None, **kw):
        cctl = Toplevel(master)
        cctl.title("Kontroldiagram " +
                   ("létrehozás" if ccparam is None else "tulajdonságok"))
        ccpanel = cls(cctl, ccparam, **kw)
        ccpanel.pack()

        Button(cctl, text="Kész", command=okcallback).pack(fill="both")
        Button(cctl, text="Mégsem", command=cctl.destroy).pack(fill="both")

        x, y = master.winfo_x(), master.winfo_y()
        cctl.update()
        w, h = cctl.winfo_width(), cctl.winfo_height()
        dx = x + w // 2
        dy = y + h // 2
        cctl.geometry(f"{w}x{h}+{dx}+{dy}")
        cctl.resizable(False, False)

        return cctl

    def _build_header_part(self):
        hf = Frame(self)
        labelconf = dict(justify="left", anchor="w", bd=1, relief="sunken", width=20)
        entryconf = dict(width=40)
        for n, (field, var) in enumerate(zip(self.fields, self.data.headervars())):
            Label(hf, text=field, cnf=labelconf
                  ).grid(row=n, column=0, sticky="news")
            e = Entry(hf, cnf=entryconf, textvariable=var)
            e.grid(row=n, column=1, sticky="news")
            self.entries[field] = e
        hf.pack()
        hf.grid_rowconfigure(0, weight=1)
        hf.grid_columnconfigure(0, weight=1)

    def _add_sep(self):
        sep = Frame(self, bd=2, relief="raised")
        sep.pack(fill="both", expand=1, ipady=2, pady=2)
        sep.grid_rowconfigure(0, weight=1)
        sep.grid_columnconfigure(0, weight=1)

    def _build_stats_part(self):
        tf = Frame(self)
        Label(tf, text="Referencia statisztikák megadása (átlag, szórás, stb.)"
              ).grid(row=0, column=0, columnspan=2, sticky="news")
        Button(tf, text="Átlag és szórás számítása", command=self._launch_refentry
               ).grid(row=1, column=0, columnspan=2, sticky="news")
        for rown, (tx, var) in enumerate(zip(
                ("Átlag", "Szórás", "Mérési bizonytalanság"),
                self.data.statvars()), start=2):

            Label(tf, text=tx, justify="left", anchor="w", bd=1, relief="sunken", width=20
                  ).grid(row=rown, column=0, sticky="news")
            Entry(tf, textvar=var, width=40
                  ).grid(row=rown, column=1, sticky="news")
        tf.pack(fill="both", expand=1)
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)

    def _launch_refentry(self):
        self.reference_entry = RefPointsTL(self, 5)
        self.reference_entry.reposition()

    def pull_data(self):
        return self.data.asvals()

    def setvars(self):
        # TODO: set CC vars and exit
        self.master.set_cc(self.pull_data())
        self.destroy()
