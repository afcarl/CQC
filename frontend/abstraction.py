from tkinter import Frame, Label, Entry


class TkTable(Frame):

    def __init__(self, master, fields, tkvars, lcnf=None, ecnf=None):
        super().__init__(master)
        self.master = master
        self.ls = []
        self.es = []
        lcnf = {} if lcnf is None else lcnf
        ecnf = {} if ecnf is None else ecnf
        w = max(len(f) for f in fields)
        for i, (fld, var) in enumerate(zip(fields, tkvars)):
            self.ls.append(Label(self, text=fld, cnf=lcnf, width=w))
            self.ls[-1].grid(row=i, column=0, sticky="news")
            self.es.append(Entry(self, textvariable=var, cnf=ecnf))
            self.es[-1].grid(row=i, column=1, sticky="news")
        for e in self.es[:-1]:
            e.bind("<Return>", self._focusjump)

    def _focusjump(self, event):
        i = self.es.index(event.widget)
        self.es[i+1].focus_set()

    def lock(self):
        for e in self.es:
            e.configure(state="disabled")

    def unlock(self):
        for e in self.es:
            e.configure(state="normal")


def replace_toplevel(master, toplevel, resizeable=False):
    x, y = master.winfo_x(), master.winfo_y()
    toplevel.update()
    w, h = toplevel.winfo_width(), toplevel.winfo_height()
    dx = x + w // 2
    dy = y + h // 2
    toplevel.geometry(f"{w}x{h}+{dx}+{dy}")
    toplevel.resizable(*[resizeable]*2)
