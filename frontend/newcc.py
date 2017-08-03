from tkinter import Frame, Label, Button
from tkinter.ttk import Treeview, Scrollbar

from dbconnection.interface import DBConnection

pkw = dict(fill="both", expand=True)
W = 40


class BuilderRoot(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.dbifc = DBConnection()
        self.data = None
        self.frameorder = [MethodFrame, ParamFrame]

        self.query_methods()
        self.frame = MethodFrame(self)
        self.frame.pack(**pkw)

        self.methods = []
        self.selections = [None, None, None]

    def stage_params(self):
        if self.frame.data is None:
            return
        self.query_params()
        if len(self.data) == 1:
            self.teardown()
            return
        self.frame.destroy()
        self.frame = ParamFrame(self)
        self.frame.pack(**pkw)

    def query_methods(self):
        t0, t1 = "Modszer", "Allomany"
        c = self.dbifc.conn.cursor()
        select = " ".join(
            (f"SELECT {t0}.id, {t0}.akkn, {t0}.name, {t1}.name",
             f"FROM {t0} INNER JOIN {t1} ON {t0}.allomany_id == {t1}.tasz")
        )
        c.execute(select)
        self.data = c.fetchall()

    def query_params(self):
        c = self.dbifc.conn.cursor()
        select = "SELECT id, name, dimension FROM Parameter WHERE modszer_id == ?"
        c.execute(select, (self.frame.data,))
        self.data = c.fetchall()

    def query_ccs(self):
        c = self.dbifc.conn.cursor()
        select = " ".join((
            "SELECT id, refmean, refstd, uncertainty, comment, parameter_id, allomany_id",
            "FROM Kontroll_diagram WHERE parameter_id == ?"
        ))
        c.execute(select, (self.frame.data,))
        self.data = c.fetchall()

    def reset(self):
        pass

    def teardown(self):
        self.query_ccs()
        print(self.data)
        self.destroy()


class StageFrameBase(Frame):

    def __init__(self, master, title, ncols, colnames, stepcb, widths, **kw):
        super().__init__(master, **kw)
        Label(self, text=title).pack(**pkw)

        self.data = None

        tw = Treeview(self, columns=[str(i) for i in range(ncols)])
        vsb = Scrollbar(self, orient="vertical", command=tw.yview)
        hsb = Scrollbar(self, orient="horizontal", command=tw.xview)

        for col, name in enumerate(colnames):
            tw.heading(f"#{col}", text=name)
        for col, cw in enumerate(widths):
            tw.column(f"#{col}", width=cw)
        for row in master.data:
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
        raise NotImplementedError


class MethodFrame(StageFrameBase):

    def __init__(self, master: BuilderRoot, **kw):
        super().__init__(master, **kw)
        Label(self, text="Mérési módszer kiválasztása").pack(**pkw)

        self.data = None

        tw = Treeview(self, columns=["akkno", "name", "owner"])
        vsb = Scrollbar(self, orient="vertical", command=tw.yview)
        hsb = Scrollbar(self, orient="horizontal", command=tw.xview)

        for col, name in enumerate(["ID", "Akkred", "Megnevezés", "Felelős"]):
            tw.heading(f"#{col}", text=name)
        for col, cw in enumerate([70, 70, 600, 200]):
            tw.column(f"#{col}", width=cw)
        for row in master.data:
            tw.insert("", "end", text=row[0], values=row[1:])

        tw.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tw.bind("<<TreeviewSelect>>", self._setdata)
        tw.pack(**pkw)
        f = Frame(self)
        Button(f, text="Mégsem", command=master.reset).pack(side="left", **pkw)
        self.nextb = Button(f, text="Tovább", command=master.stage_params, state="disabled")
        self.nextb.pack(side="left", **pkw)
        f.pack(**pkw)

    def _setdata(self, event):
        sel = event.widget.selection(items="#0")
        self.data = event.widget.item(sel)["text"]
        self.nextb.configure(state="active")
        print(self.data)


class ParamFrame(Frame):

    def __init__(self, master: BuilderRoot, **kw):
        super().__init__(master, **kw)

        Label(self, text="Kontrollált paraméter kiválasztása").pack(**pkw)

        self.data = None

        tw = Treeview(self, columns=["parameter", "dimension"])
        vsb = Scrollbar(self, orient="vertical", command=tw.yview)
        hsb = Scrollbar(self, orient="horizontal", command=tw.xview)

        for col, name in enumerate(["ID", "Paraméter", "Mértékegység"]):
            tw.heading(f"#{col}", text=name)
        for col, cw in enumerate([70, 600, 200]):
            tw.column(f"#{col}", width=cw)
        for row in master.data:
            tw.insert("", "end", text=row[0], values=row[1:])

        tw.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tw.bind("<<TreeviewSelect>>", self._setdata)
        tw.pack(**pkw)
        f = Frame(self)
        Button(f, text="Mégsem", command=master.reset).pack(side="left", **pkw)
        self.nextb = Button(f, text="Tovább", command=master.teardown, state="disabled")
        self.nextb.pack(side="left", **pkw)
        f.pack(**pkw)

    def _setdata(self, event):
        sel = event.widget.selection(items="#0")
        self.data = event.widget.item(sel)["text"]
        self.nextb.configure(state="active")
        print(self.data)


class CCFrame(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        Label(self, text="Kontrollált paraméter kiválasztása").pack(**pkw)

        tw = Treeview(self, columns=["parameter", "dimension"])
        vsb = Scrollbar(self, orient="vertical", command=tw.yview)
        hsb = Scrollbar(self, orient="horizontal", command=tw.xview)

        for col, name in enumerate(["ID", "Paraméter", "Mértékegység"]):
            tw.heading(f"#{col}", text=name)
        for col, cw in enumerate([70, 600, 200]):
            tw.column(f"#{col}", width=cw)
        for row in master.data:
            tw.insert("", "end", text=row[0], values=row[1:])

        tw.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tw.bind("<<TreeviewSelect>>", self._setdata)
        tw.pack(**pkw)
        f = Frame(self)
        Button(f, text="Mégsem", command=master.reset).pack(side="left", **pkw)
        self.nextb = Button(f, text="Tovább", command=master.teardown, state="disabled")
        self.nextb.pack(side="left", **pkw)
        f.pack(**pkw)

    def _setdata(self, event):
        pass


if __name__ == '__main__':
    from tkinter import Tk
    tk = Tk()
    br = BuilderRoot(tk)
    br.pack(**pkw)
    tk.mainloop()
