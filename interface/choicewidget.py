from tkinter import Frame, Label, Button
from tkinter.ttk import Treeview, Scrollbar

from util import pkw


class ChoiceCallbacks:

    def __init__(self, stepcb=None, newcb=None, backcb=None, cancelcb=None):
        self.step = stepcb
        self.new = newcb
        self.back = backcb
        self.cancel = cancelcb
        self.__dict__.update({k[:-2]: v for k, v in locals().items() if k != "self"})

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        if key not in self.__dict__:
            raise KeyError("No such field: " + str(key))
        self.__dict__[key] = value


class TkChoice(Frame):

    def __init__(self, master, arg, data, callbacks):
        super().__init__(master)
        title, colnames, widths = arg
        self.data = None
        self.tw = None

        Label(self, text=title + " kiválasztása").pack(**pkw)

        self._build_treeview(data, colnames, widths, callbacks)
        self._build_buttonframe(callbacks, title)

    def _build_treeview(self, data, colnames, widths, callbacks):
        self.tw = Treeview(self, columns=[str(i) for i in range(len(colnames)-1)])
        self._configure_treeview(data, colnames, widths)
        self._add_scrollbar_to_treeview()

        self.tw.bind("<<TreeviewSelect>>", self.setdata)
        self.tw.bind("<Double-Button-1>", callbacks["step"])
        self.tw.pack(**pkw)

    def _configure_treeview(self, data, colnames, widths):
        for col, name in enumerate(colnames):
            self.tw.heading(f"#{col}", text=name)
        for col, cw in enumerate(widths):
            self.tw.column(f"#{col}", width=cw)
        for row in data:
            self.tw.insert("", "end", text=row[0], values=row[1:])

    def _add_scrollbar_to_treeview(self):
        vsb = Scrollbar(self, orient="vertical", command=self.tw.yview)
        self.tw.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", **pkw)

    def _build_buttonframe(self, callbacks, title):
        f = Frame(self)
        if callbacks["back"]:
            Button(f, text="Vissza", command=callbacks["back"]).pack(side="left", **pkw)
        if callbacks["cancel"]:
            Button(f, text="Mégsem", command=callbacks["cancel"]).pack(side="left", **pkw)
        if callbacks["new"]:
            Button(f, text=f"Új {title.lower()}...", command=callbacks["new"]).pack(side="left", **pkw)
        self.nextb = Button(f, text="Tovább", command=callbacks["step"], state="disabled")
        self.nextb.pack(side="left", **pkw)
        f.pack(**pkw)

    def setdata(self, event):
        sel = event.widget.selection(items="#0")
        self.data = event.widget.item(sel)["text"]
        self.nextb.configure(state="active")
