import sqlite3 as sql

from util.const import DBPATH


class DBConnection:
    """
    Modszer -E Parameter -E Kontroll_diagram -E Kontroll_meres
    """
    conn = sql.connect(DBPATH)
    c = conn.cursor()
    x = c.execute

    def get_username(self, ID, alias=0):
        col = ["name", "alias1", "alias2"]
        got = self.query(f"SELECT {col[alias]} FROM Staff WHERE id == ?;", [ID])
        return got[0][0] if got else ""

    def get_userid(self, name):
        self.x("SELECT id FROM Staff WHERE name == ? OR alias1 == ? OR alias2 == ?;",
               [name] * 3)
        results = self.c.fetchall()
        if len(results) > 1:
            print(f"Multiple ID values for NAME: {name} - {', '.join(r[0] for r in results)}")
        return results[0][0]

    def query(self, select, args=()):
        self.x(select, args)
        return list(self.c.fetchall())

    def insert(self, tablename, keys, values):
        assert len(keys) == len(values)
        sqlcmd = f"INSERT INTO {tablename} ({', '.join(keys)}) " + \
                 f"VALUES ({', '.join('?' for _ in range(len(keys)))});"
        print("Running insert:", sqlcmd, "\n", values)
        with self.conn:
            self.x(sqlcmd, values)

    def push_record(self, recobj):
        keys, values = list(zip(
            *[[key, val] for key, val in recobj.data.items() if val is not None]
        ))
        self.insert(recobj.table, keys, values)
        return self.c.lastrowid

    def push_object(self, ccobj):
        IDs = {k: None for k in ccobj.stages}
        uID = None
        for stage in ccobj.stages:
            rec = ccobj.rec[stage]
            IDs[stage] = rec["id"]
            if rec["id"] is not None:
                uID = rec["id"]
                continue
            rec.upstream_id = uID
            uID = self.push_record(rec)
            print("Saved", stage)
        return IDs

    def push_measurements(self, meas):
        fields = ','.join(meas.fields[1:])
        qmarks = ','.join('?' for _ in range(len(meas['value'])))
        insert = f"INSERT INTO Control_measurement ({fields}) VALUES ({qmarks})"
        data = meas.asmatrix(transpose=True)
        self.c.executemany(insert, data)

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
