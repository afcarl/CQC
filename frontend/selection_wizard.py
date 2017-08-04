from tkinter import Toplevel, Frame, Label, Button, messagebox as tkmb
from tkinter.ttk import Treeview, Scrollbar


from dbconnection.interface import DBConnection


pkw = dict(fill="both", expand=True)


class SelectionWizard(Toplevel):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.dbifc = DBConnection()
        self.data = dict(
            method=[],
            param=[],
            cc=[]
        )
        self.selection = dict(
            method=None,
            param=None,
            cc=None
        )
        self.arg = dict(
            method=("Mérési módszer kiválasztása",
                    ["ID", "Akkred", "Megnevezés", "Felelős"],
                    [70, 70, 600, 200], self.stage_params),
            param=("Kontrollált paraméter kiválasztása",
                   ["ID", "Paraméter", "Mértékegység"],
                   [70, 600, 200], self.stage_ccs),
            cc=("Kontroll diagram kiválasztása",
                ["ID", "Anyagminta", "Dátum", "Felvevő", "Megjegyzés"],
                [70, 100, 100, 300, 500], self.stage_final)
        )
        self.result = None
        self.query_methods()
        self.frame = StageFrame(self, "method")
        self.frame.pack(**pkw)
        self.methods = []

    def stage_params(self):
        if self.selection["method"] is None:
            self.selection["method"] = self.frame.data
        self.query_params()
        data = self.data["param"]
        if len(data) == 1:
            self.selection["param"] = data[0][0]
            self.stage_ccs()
            return
        elif len(data) == 0:
            msg = "A választott módszerhez nincs rögzítve paraméter!"
            tkmb.showinfo("Információ", msg)
            self.teardown()
            return
        self.frame.destroy()
        self.frame = StageFrame(self, "param")
        self.frame.pack(**pkw)

    def stage_ccs(self):
        if self.selection["param"] is None:
            self.selection["param"] = self.frame.data
        self.query_ccs()
        data = self.data["cc"]
        if len(data) == 1:
            self.selection["cc"] = data[0][0]
            self.stage_final()
            return
        elif len(data) == 0:
            msg = "A választott paraméterhez nem tartozik kontroll diagram!"
            tkmb.showinfo("Információ", msg)
            self.teardown()
            return
        self.frame.destroy()
        self.frame = StageFrame(self, "cc")
        self.frame.pack(**pkw)

    def stage_final(self):
        if self.selection["cc"] is None:
            self.selection["cc"] = self.frame.data
        self.teardown()

    def query_methods(self):
        t0, t1 = "Modszer", "Allomany"
        select = " ".join(
            (f"SELECT {t0}.id, {t0}.akkn, {t0}.name, {t1}.name",
             f"FROM {t0} INNER JOIN {t1} ON {t0}.allomany_id == {t1}.tasz")
        )
        self.dbifc.x(select)
        self.data["method"] = self.dbifc.c.fetchall()

    def query_params(self):
        select = "SELECT id, name, dimension FROM Parameter WHERE modszer_id == ?"
        self.dbifc.x(select, (self.selection["method"],))
        self.data["param"] = self.dbifc.c.fetchall()

    def query_ccs(self):
        t0 = "Kontroll_diagram"
        t1 = "Allomany"
        select = " ".join((
            f"SELECT {t0}.id, {t0}.refmaterial, {t0}.startdate, {t1}.name, {t0}.comment",
            f"FROM {t0} INNER JOIN {t1} ON {t0}.allomany_id == {t1}.tasz",
            f"WHERE {t0}.parameter_id == ?;"
        ))
        self.dbifc.x(select, (self.selection["param"],))
        self.data["cc"] = self.dbifc.c.fetchall()

    def reset(self):
        pass

    def teardown(self):
        self.destroy()


class StageFrame(Frame):

    def __init__(self, master, frametype):
        super().__init__(master)
        title, colnames, widths, stepcb = master.arg[frametype]
        data = master.data[frametype]

        Label(self, text=title).pack(**pkw)

        self.data = None

        tw = Treeview(self, columns=[str(i) for i in range(len(colnames)-1)])
        vsb = Scrollbar(self, orient="vertical", command=tw.yview)
        hsb = Scrollbar(self, orient="horizontal", command=tw.xview)

        for col, name in enumerate(colnames):
            tw.heading(f"#{col}", text=name)
        for col, cw in enumerate(widths):
            tw.column(f"#{col}", width=cw)
        for row in data:
            tw.insert("", "end", text=row[0], values=row[1:])

        tw.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tw.bind("<<TreeviewSelect>>", self._setdata)
        tw.pack(**pkw)
        f = Frame(self)
        Button(f, text="Mégsem", command=master.reset).pack(side="left", **pkw)
        self.nextb = Button(f, text="Tovább", command=stepcb, state="disabled")
        self.nextb.pack(side="left", **pkw)
        f.pack(**pkw)

    def _setdata(self, event):
        sel = event.widget.selection(items="#0")
        self.data = event.widget.item(sel)["text"]
        self.nextb.configure(state="active")
        print(self.data)


if __name__ == '__main__':
    SelectionWizard(None).mainloop()
