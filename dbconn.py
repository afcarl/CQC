from __future__ import print_function, absolute_import, unicode_literals

import sqlite3 as sql

testroot = "/home/csa/SciProjects/Project_CQC/"


class MetaHandler(object):

    @staticmethod
    def read(path):
        try:
            with open(path) as fileobj:
                data = fileobj.read()
        except FileNotFoundError:
            print("MetaHandler: no metadata file :(")
            return {}
        lines = data.split("\n")
        mapping = {k.strip(): v.strip() for k, v in [line.split(":") for line in lines if line]}
        return mapping


# noinspection PyUnresolvedReferences
class DBConnection(object):

    def __init__(self, dbpath, metapath):
        self.__dict__.update(MetaHandler.read(metapath))
        self.__dict__.update({k: v for k, v in locals().items() if k != "self"})
        self.methods = []
        self.conn = sql.connect(dbpath)
        self.x = self.conn.execute
        self.create_db()

    def create_db(self):
        cctable_fields = [
            "cc_id TEXT PRIMARY KEY NOT NULL",
            "paramname TEXT NOT NULL",
            "dimension TEXT",
            "refmean REAL NOT NULL",
            "refstd REAL NOT NULL",
            "uncertainty REAL NOT NULL"
        ]
        datatable_fields = [
            "pnt_id INT PRIMARY KEY",
            "cc_id TEXT NOT NULL",
            "date INT NOT NULL",
            "value REAL NOT NULL",
            "FOREIGN KEY(cc_id) REFERENCES Kontroll_diagram(cc_id)"
        ]

        create_cctable = ("CREATE TABLE IF NOT EXISTS Kontroll_diagram ({});"
                          .format(", ".join(cctable_fields)))
        create_datatable = ("CREATE TABLE IF NOT EXISTS Referencia_meres ({});"
                            .format(", ".join(datatable_fields)))
        with self.conn:
            self.x(create_cctable)
            self.x(create_datatable)

    def new_cc(self, cc_object):
        insert = "INSERT INTO Kontroll_diagram VALUES (?,?,?,?,?,?)"
        params = cc_object.tabledata()
        with self.conn:
            self.x(insert, params)

    def delete_cc(self, cc_object):
        delete_data = "DELETE * FROM Referencia_meres WHERE cc_id == ?;"
        delete_cc = "DELETE * FROM Kontroll_diagram WHERE cc_id == ?;"
        with self.conn:
            self.x(delete_data, [cc_object.ID])
            self.x(delete_cc, [cc_object.ID])

    def update_cc(self, cc_object):
        update = "UPDATE Kontrol_diagram SET "
        update += "paramname = ?, dimension = ?, refmean = ?, refstd = ?, uncertainty = ? "
        update += "WHERE cc_id = ?;"
        params = cc_object.tabledata()
        params.append(params.pop(0))  # rotate list, so cc_id is the last element
        with self.conn:
            self.x(update, params)

    def add_measurements(self, cc_ID, dates, points):
        insert = "INSERT INTO Referencia_meres VALUES (?,?,?)"
        with self.conn:
            self.conn.executemany(insert, ((cc_ID, d, p) for d, p in zip(dates, points)))

    def truncate_measurements(self, cc_ID):
        delete = "DELETE * FROM Referencia_meres WHERE cc_id == ?;"
        with self.conn:
            self.x(delete, cc_ID)

    def modify_measurements(self, cc_ID, dates, points):
        self.truncate_measurements(cc_ID)
        self.add_measurements(cc_ID, dates, points)


def main():
    import numpy as np

    from CQC.cchart import ControlChart

    dbc = DBConnection(testroot + "TestDb.db", testroot + "meta.dat")
    # dbc.create_db()

    N = 100
    dates = np.linspace(0, 100, N)
    mn, st, unc = 10., 3., 10.
    points = (np.random.randn(N) * st) + mn
    cc = ControlChart(method_ID="NAVSZI_123", etalon_ID="BFG 9000",
                      paramname="TesztParaméter", dimension="m/s**2")
    cc.reference_from_stats(mn, st, unc)
    dbc.new_cc(cc)
    cc.add_points(dates, points, dbhandle=dbc)
    cc.report()


def printout_db():

    def stringify_table(tablename):
        chain = "TABLE: {}\n".format(tablename)
        chain += "-" * 30 + "\n"
        c.execute("SELECT * FROM " + tablename)
        chain += "\n".join(", ".join(map(str, line)) for line in c)
        return chain

    dbc = DBConnection(testroot + "TestDb.db", testroot + "meta.dat")
    c = dbc.conn.cursor()
    kd = "Kontroll_diagram"
    rm = "Referencia_meres"
    outchain = "\n\n".join((stringify_table(kd), stringify_table(rm)))
    print(outchain)

if __name__ == '__main__':
    printout_db()
