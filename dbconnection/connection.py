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
        t0, t1 = "Kontroll_diagram", "Allomany"
        ccol = ["startdate", "refmaterial", "comment", "refmean", "refstd", "uncertainty"]
        c0 = ", ".join(t0 + "." + c for c in ccol)
        c1 = "Allomany.name"
        select = " ".join((
            f"SELECT {c1}, {c0} FROM {t0} INNER JOIN {t1}",
            f"ON {t0}.allomany_id == {t1}.tasz",
            f"WHERE {t0}.id == ?"
        ))
        self.x(select, [ccID])
        return dict(zip(["ccowner"] + ccol, self.c.fetchone()))

    def get_methodparam(self, ccID):
        t1, t2, t3 = "Parameter", "Modszer", "Allomany"
        c1 = ", ".join(t1 + "." + c for c in ("name", "dimension"))
        c2 = ", ".join(t2 + "." + c for c in ("akkn", "name"))
        c3 = ", ".join(t3 + "." + c for c in ("name",))
        select = " ".join((
            f"SELECT {c1}, {c2}, {c3} FROM {t1}",
            f"INNER JOIN {t2} ON {t1}.modszer_id == {t2}.id",
            f"INNER JOIN {t3} ON {t2}.allomany_id == {t3}.tasz",
            f"WHERE {t1}.id ==",
            f"(SELECT parameter_id FROM Kontroll_diagram WHERE id == ?);"
        ))
        self.x(select, [ccID])
        data = dict(zip(["paramname", "dimension", "akkn", "methodname", "methodowner"],
                        self.c.fetchone()))
        return data

    def new_cc(self, cc_object):
        insert = f"INSERT INTO Kontroll_diagram VALUES ({','.join('?'*8)})"
        params = cc_object.tabledata()
        with self.conn:
            self.x(insert, params)

    def delete_cc(self, ccID):
        delete_data = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        delete_cc = "DELETE * FROM Kontroll_diagram WHERE id == ?;"
        with self.conn:
            self.x(delete_data, [ccID])
            self.x(delete_cc, [ccID])

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
