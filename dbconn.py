from __future__ import print_function, absolute_import, unicode_literals

import sqlite3 as sql


class MetaHandler(object):

    @staticmethod
    def read(path):
        with open(path) as fileobj:
            data = fileobj.read()
        lines = data.split("\n")
        mapping = {k: v for k, v in [line.split(": ") for line in lines if line]}
        return mapping


# noinspection PyUnresolvedReferences
class DBConnection(object):

    def __init__(self, dbpath, metapath):
        self.__dict__.update(MetaHandler.read(metapath))
        self.__dict__.update({k: v for k, v in locals().items() if k != "self"})
        self.methods = []
        self.conn = sql.connect(dbpath)
        self.x = self.conn.execute

    def create_db(self):
        cctable_fields = [
            "cc_id TEXT PRIMARY KEY NOT NULL",
            "paramname TEXT NOT NULL",
            "dimension TEXT",
            "refmean REAL NOT NULL",
            "refstd REAL NOT NULL"
        ]
        datatable_fields = [
            "msr_id TEXT PRIMARY KEY NOT NULL",
            "cc_id TEXT NOT NULL",
            "date INT NOT NULL",
            "value REAL NOT NULL"
        ]
        create_cctable = ("CREATE TABLE Kontroll_diagram ({});"
                          .format(", ".join(cctable_fields)))
        create_datatable = ("CREATE TABLE Referencia_meres ({});"
                            .format(", ".join(datatable_fields)))

        # CTXMGR autocommits / rolls back in case of success / error
        with self.conn:
            self.x(create_cctable)
            self.x(create_datatable)

    def new_cc(self, cc_object):
        insert = "INSERT INTO Kontroll_diagram VALUES (?,?,?,?)"
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
        update += "paramname = ?, dimension = ?, refmean = ?, refstd = ? "
        update += "WHERE cc_id = ?;"
        params = cc_object.tabledata()
        params.append(params.pop(0))
        with self.conn:
            self.x(update, params)

    def add_measurements(self, cc_ID, dates, points):
        insert = "INSERT INTO Referencia_meres VALUES (?,?,?)"
        with self.conn:
            self.conn.executemany(insert, ((cc_ID, d, p) for d, p in zip(dates, points)))

    def delete_measurements(self, cc_ID, dates):
        delete = "DELETE * FROM Referencia_meres WHERE cc_ID = ? AND date = ?"
        with self.conn:
            self.conn.executemany(delete, ((cc_ID, d) for d in dates))

    def modify_measurements(self, cc_ID, dates, points):
        update = "UPDATE Referencia_meres SET"
