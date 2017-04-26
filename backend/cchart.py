from __future__ import print_function, unicode_literals, absolute_import

from datetime import datetime

import numpy as np


class ControlChart(object):

    def __init__(self, method_ID, etalon_ID, paramname, dimension,
                 revision=1, startdate=None):
        self.method_ID = method_ID
        self.etalon_ID = etalon_ID
        self.revision = revision
        self.ID = "KD-{}-{}-{}".format(method_ID, etalon_ID, revision)
        self.paramname = paramname
        self.dimension = dimension
        self.startdate = datetime.today() if startdate is None else startdate
        self.datemin = 0
        self.datemax = 0

        self.refmean = None
        self.refstd = None
        self.uncertainty = None
        self.dates = np.array([])
        self.points = np.array([])

    @classmethod
    def from_database(cls, ID, dbhandle):
        select_cc = "SELECT * FROM Kontroll_diagram WHERE cc_ID == ?;"
        select_data = "SELECT date, value FROM Referencia_meres WHERE cc_ID == ?;"
        c = dbhandle.conn.cursor()
        c.execute(select_cc, [ID])
        args = c.fetchone()
        c.execute(select_data, [ID])
        dates, points = list(*zip([d for d in c]))

        cc = ControlChart(*args[1:])
        cc.add_points(dates, points)

        return cc

    def reference_from_points(self, refpoints):
        self.refmean = refpoints.mean()
        self.refstd = refpoints.std()

    def reference_from_stats(self, refmean, refstd, uncertainty=None):
        self.refmean = refmean
        self.refstd = refstd
        self.uncertainty = uncertainty

    def calculate_uncertainty(self, points):
        std = np.std(points)
        self.uncertainty = std / len(points)

    def add_points(self, dates,  points):
        err = " ".join(("Unitialized control chart!",
                        "Please supply a reference mean,",
                        "standard deviation and measurement uncertainty!"))
        if any(map(lambda x: x is None, (self.refmean, self.refstd, self.uncertainty))):
            raise RuntimeError(err)
        if isinstance(points, np.ndarray):
            points = points.tolist()
        if isinstance(dates, np.ndarray):
            dates = dates.tolist()
        self.points = np.append(self.points, points)
        self.dates = np.append(self.dates, dates)
        self.datemin = np.min(self.dates)
        self.datemax = np.max(self.dates)

    def delete_points(self, dates):
        self.points = self.points[self.dates != dates]
        self.dates = self.dates[self.dates != dates]

    def modify_points(self, dates, points):
        self.points[self.dates == dates] = points

    def report(self):
        chain = "Kontroll diagram {}\n".format(self.ID)
        chain += "-"*len(chain) + "\n"
        chain += "Paraméter: {}\n".format(self.paramname)
        chain += "Etalon: {}\n".format(self.etalon_ID)
        chain += "{}. revízió\n".format(self.revision)
        chain += "{} -- {}\n".format(self.datemin, self.datemax)
        print(chain)
        return chain

    def tabledata(self):
        out = [self.ID, self.paramname, self.dimension,
               self.refmean, self.refstd, self.uncertainty]
        return out
