from tkinter import Toplevel, messagebox as tkmb

from dbconnection import DBConnection
from interface.choicewidget import TkChoice
from util import pkw


# noinspection PyUnusedLocal
class SelectionWizard(Toplevel):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.title("Kontroll diagram megnyitása...")
        self.dbifc = DBConnection()
        self.data = {}
        self.selection = {}
        self.arg = {}
        self.stage = None
        self.frame = None
        self.callbacks = dict(back=self.reset, cancel=self.teardown, new=self.new)
        self.reset()

    def stage_params(self, event=None):
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
            self.destroy()
            return
        self.stage = "param"
        self.frame.destroy()
        self.frame = TkChoice(self, self.arg[self.stage], self.data[self.stage],
                              dict(step=self.stage_ccs, **self.callbacks))
        self.frame.pack(**pkw)

    def stage_ccs(self, event=None):
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
            self.selection["cc"] = None
            self.destroy()
            return
        self.stage = "cc"
        self.frame.destroy()
        self.frame = TkChoice(self, self.arg[self.stage], self.data[self.stage],
                              dict(step=self.stage_final, **self.callbacks))
        self.frame.pack(**pkw)

    def stage_final(self, event=None):
        if self.selection["cc"] is None:
            self.selection["cc"] = self.frame.data
        self.destroy()

    def query_methods(self):
        t0, t1 = "Method", "Staff"
        select = " ".join((
            f"SELECT {t0}.id, {t0}.akkn, {t0}.name, {t1}.name",
            f"FROM {t0} INNER JOIN {t1} ON {t0}.staff_id == {t1}.tasz"
        ))
        self.dbifc.x(select)
        self.data["method"] = self.dbifc.c.fetchall()

    def query_params(self):
        select = "SELECT id, name, dimension FROM Parameter WHERE method_id == ?"
        self.dbifc.x(select, (self.selection["method"],))
        self.data["param"] = self.dbifc.c.fetchall()

    def query_ccs(self):
        t0 = "Control_chart"
        t1 = "Staff"
        select = " ".join((
            f"SELECT {t0}.id, {t0}.refmaterial, {t0}.startdate, {t1}.name, {t0}.comment",
            f"FROM {t0} INNER JOIN {t1} ON {t0}.staff_id == {t1}.tasz",
            f"WHERE {t0}.parameter_id == ?;"
        ))
        self.dbifc.x(select, (self.selection["param"],))
        self.data["cc"] = self.dbifc.c.fetchall()

    def logical_reset(self):
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
                    [70, 70, 600, 200]),
            param=("Kontrollált paraméter kiválasztása",
                   ["ID", "Paraméter", "Mértékegység"],
                   [70, 600, 200]),
            cc=("Kontroll diagram kiválasztása",
                ["ID", "Anyagminta", "Dátum", "Felvevő", "Megjegyzés"],
                [70, 100, 100, 300, 500])
        )
        self.stage = "method"
        self.query_methods()

    def ui_reset(self):
        if self.frame is not None:
            self.frame.destroy()
        self.frame = TkChoice(self, self.arg[self.stage], self.data[self.stage],
                              dict(step=self.stage_params, **self.callbacks))
        self.frame.pack(**pkw)

    def reset(self):
        self.logical_reset()
        self.ui_reset()

    def teardown(self):
        self.logical_reset()
        self.destroy()

    def new(self):
        print("Called <new> @ stage:", self.stage)


if __name__ == '__main__':
    SelectionWizard(None).mainloop()
