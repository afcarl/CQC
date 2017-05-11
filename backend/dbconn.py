from __future__ import print_function, absolute_import, unicode_literals

import sqlite3 as sql


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
        mapping = {
            k.strip(): v.strip() for k, v in
            [line.split(":") for line in lines if line]
        }
        return mapping


class DBConnection(object):

    def __init__(self, dbpath, metapath):
        self.__dict__.update(MetaHandler.read(metapath))
        self.__dict__.update({k: v for k, v in locals().items() if k != "self"})
        self.methods = []
        self.conn = sql.connect(dbpath)
        self.x = self.conn.execute

    def get_ccs(self, mnum):
        c = self.conn.cursor()
        t0 = "Kontroll_diagram"
        t1 = "Kontrolld_Modszer_kapcsolo"
        c0 = ("id", "paramname", "dimension", "refmean",
              "refstd", "uncertainty", "comment")
        select = ("SELECT " + ", ".join(t0 + "." + c for c in c0) +
                  f"FROM {t0} INNER JOIN {t1} ON {t0}.id == {t1}.djnum" +
                  f"WHERE {t1}.djnum == ?;")
        c.execute(select, mnum)
        return list(c.fetchall())

    def new_cc(self, cc_object):
        insert = f"INSERT INTO Kontroll_diagram VALUES ({','.join('?'*8)})"
        params = cc_object.tabledata()
        with self.conn:
            self.x(insert, params)

    def delete_cc(self, cc_object):
        delete_data = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        delete_cc = "DELETE * FROM Kontroll_diagram WHERE id == ?;"
        with self.conn:
            self.x(delete_data, [cc_object.ID])
            self.x(delete_cc, [cc_object.ID])

    def update_cc(self, cc_object):
        update = "UPDATE Kontrol_diagram SET "
        update += "paramname = ?, dimension = ?, refmean = ?, refstd = ?, uncertainty = ? "
        update += "WHERE id = ?;"
        params = cc_object.tabledata()
        params.append(params.pop(0))  # rotate list, so id is the last element
        with self.conn:
            self.x(update, params)

    def add_measurements(self, cc_ID, dates, points):
        insert = "INSERT INTO Kontroll_meres VALUES (?,?,?)"
        with self.conn:
            self.conn.executemany(insert, ((cc_ID, d, p) for d, p in zip(dates, points)))

    def delete_measurements(self, cc_ID):
        delete = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        with self.conn:
            self.x(delete, cc_ID)

    def modify_measurements(self, cc_ID, dates, points):
        self.delete_measurements(cc_ID)
        self.add_measurements(cc_ID, dates, points)
