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

    def get_methods(self):
        c = self.conn.cursor()
        select = "SELECT id, name, mnum, akkn, allomany_id FROM Modszer"
        c.execute(select)
        return list(c.fetchall())

    def get_params(self, mID):
        c = self.conn.cursor()
        t0 = "Parameter"
        t1 = "Modszer"
        select = (f"SELECT {t0}.id, {t0}.name, {t0}.dimension FROM",
                  f"{t0} INNER JOIN {t1} ON {t1}.id == {t0}.modszer_id",
                  f"WHERE {t1}.id == ?;")
        c.execute(" ".join(select), [mID])
        return list(c.fetchall())

    def get_ccs(self, pID):
        c = self.conn.cursor()
        cct = "Kontroll_diagram"
        pt = "Parameter"
        ccf = ", ".join(cct + "." + c for c in
                        ("id", "refmean", "refstd", "uncertainty", "comment"))
        pf = ", ".join(pt + "." + c for c in ("id", "name", "dimension"))
        select = " ".join(
            ((f"SELECT {ccf}, {pf} FROM",
              f"{cct} INNER JOIN {pt} ON {cct}.parameter_id == {pt}.id",
              f"WHERE {pt}.id == ?;"))
        )
        c.execute(select, [pID])
        return list(c.fetchall())

    def get_measurements(self, ccID):
        c = self.conn.cursor()
        t0 = "Kontroll_diagram"
        t1 = "Kontroll_meres"
        c1 = ", ".join(t1 + "." + c for c in ("id", "date", "value", "comment"))
        select = (f"SELECT {c1} FROM",
                  f"{t1} INNER JOIN {t0} ON {t0}.id == {t1}.kontroll_diagram_id",
                  f"WHERE {t0}.id == ?;")
        c.execute(" ".join(select), [ccID])
        points = list(c.fetchall())
        return points if points else None

    def get_username(self, tasz):
        c = self.conn.cursor()
        c.execute("SELECT name FROM Allomany WHERE tasz == ?;", (tasz,))
        return c.fetchone()[0]

    def get_ccparam(self, ccID):
        select = "SELECT * FROM Kontroll_diagram WHERE id == ?;"
        self.x(select, [ccID])
        fields = ("cc_id", "startdate", "refmaterial", "refmean", "refstd",
                  "uncertainty", "comment", "parameter_id", "allomany_id")
        return dict(zip(fields, self.c.fetchone()))

    def get_paramparam(self, pID):
        select = "SELECT * FROM Parameter WHERE id == ?;"
        self.x(select, [pID])
        fields = ("parameter_id", "paramname", "dimension", "modszer_id")
        return dict(zip(fields, self.c.fetchone()))

    def get_methodparam(self, mID):
        fields = ("modszer_id", "methodname", "mnum", "akkn", "allomany_id")
        select = "SELECT * FROM Modszer WHERE id == ?;"
        self.x(select, [mID])
        data = self.c.fetchone()
        return dict(zip(fields, data))

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
