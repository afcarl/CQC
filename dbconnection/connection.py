import sqlite3 as sql

from util.const import DBPATH, METAPATH


def read_meta(path):
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


class DBConnection:
    """
    Modszer -E Parameter -E Kontroll_diagram -E Kontroll_meres
    """

    conn = sql.connect(DBPATH)
    c = conn.cursor()
    x = c.execute
    meta = read_meta(METAPATH)

    def get_username(self, tasz, alias=0):
        col = ["name", "alias1", "alias2"]
        c = self.conn.cursor()
        c.execute(f"SELECT {col[alias]} FROM Allomany WHERE tasz == ?;", [tasz])
        return c.fetchone()[0]

    def get_tasz(self, name):
        self.x("SELECT tasz FROM Staff WHERE name == ? OR alias1 == ? OR alias2 == ?;",
               [name] * 3)
        return self.c.fetchone()[0]

    def get_measurements(self, ccID):
        self.x("SELECT * FROM Control_measurement WHERE cc_id == ?;" [ccID])
        return list(self.c.fetchall())

    def new_cc(self, ccobj):
        par = ccobj.parameter
        fields = par.ccfields + par.statfields
        insert = " ".join((
            f"INSERT INTO Kontroll_diagram ({', '.join(fields)}) VALUES",
            f"({', '.join(['?'*len(fields)])});"
        ))
        with self.conn:
            self.x(insert, (par[f] for f in fields))

    def delete_cc(self, ccID):
        delete_data = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        delete_cc = "DELETE * FROM Kontroll_diagram WHERE id == ?;"
        with self.conn:
            self.x(delete_data, [ccID])
            self.x(delete_cc, [ccID])

    def update_cc(self, ccobj):
        par = ccobj.param
        fields = ("startdate", "refmaterial", "refmean", "refstd", "uncertainty",
                  "comment", "parameter_id", "allomany_id")
        update = " ".join((
            "UPDATE Kontroll_diagram SET ",
            ", ".join(f"{f} = ?" for f in fields),
            "WHERE id = ?"
        ))
        vals = [par[f].get() for f in fields + ("ccID",)]
        vals[2:5] = list(map(float, vals[2:5]))
        with self.conn:
            self.x(update, vals)

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
