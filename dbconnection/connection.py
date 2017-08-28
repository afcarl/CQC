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
    _currentuser = None

    def current_user(self, gettasz=False):
        if self._currentuser is None:
            import getpass
            tasz = getpass.getuser()
            if not tasz.isdigit():
                tasz = "315855"
            self.x("SELECT * FROM Staff WHERE tasz == ?;", [tasz])
            self._currentuser = self.c.fetchone()
        return self._currentuser[int(not gettasz)]

    def get_username(self, tasz, alias=0):
        col = ["name", "alias1", "alias2"]
        c = self.conn.cursor()
        c.execute(f"SELECT {col[alias]} FROM Staff WHERE tasz == ?;", [tasz])
        return c.fetchone()[0]

    def get_tasz(self, name):
        self.x("SELECT tasz FROM Staff WHERE name == ? OR alias1 == ? OR alias2 == ?;",
               [name] * 3)
        results = self.c.fetchall()
        if len(results) > 1:
            print(f"Multiple TASZ values for NAME: {name} - {', '.join(r[0] for r in results)}")
        return results[0][0]

    def query(self, select, args):
        self.x(select, args)
        return list(self.c.fetchall())

    def new_cc(self, ccobj):
        ccr = ccobj.ccrec
        insert = " ".join((
            f"INSERT INTO Kontroll_diagram ({', '.join(ccr.fields)}) VALUES",
            f"({', '.join(['?'*len(ccr.data)])});"
        ))
        with self.conn:
            self.x(insert, ccr.asvals())

    def delete_cc(self, ccID):
        delete_data = "DELETE * FROM Kontroll_meres WHERE cc_id == ?;"
        delete_cc = "DELETE * FROM Kontroll_diagram WHERE id == ?;"
        with self.conn:
            self.x(delete_data, [ccID])
            self.x(delete_cc, [ccID])

    def update_cc(self, ccobj):
        ccr = ccobj.ccrec
        update = " ".join((
            "UPDATE Control_chart SET ",
            ", ".join(f"{f} = ?" for f in ccr.fields[1:]),
            "WHERE id = ?"
        ))
        vals = [ccobj.ccrec[f] for f in ccr.fields[1:] + ("id",)]
        vals[-4:-1] = map(float, vals[-4:-1])
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
