from __future__ import print_function, unicode_literals, absolute_import

import numpy as np


class ControlChart(object):

    def __init__(self, method_ID, etalon_ID, paramname, dimension, revision=1):
        self.method_ID = method_ID
        self.etalon_ID = etalon_ID
        self.revision = revision
        self.ID = "KD-{}-{}-{}".format(method_ID, etalon_ID, revision)
        self.paramname = paramname
        self.dimension = dimension
        self.datemin = 0
        self.datemax = 0

        self.refmean = None
        self.refstd = None
        self.uncertainty = None
        self.dates = np.array([])
        self.points = np.array([])

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

    def add_points(self, dates,  points, dbhandle=None):
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
        if dbhandle is not None:
            dbhandle.add_measurements(self.ID, dates, points)

    def delete_points(self, dates, dbhandle=None):
        self.points = self.points[self.dates != dates]
        self.dates = self.dates[self.dates != dates]
        dbhandle.modify_measurements(self.ID, self.dates, self.points)

    def modify_points(self, dates, points, dbhandle=None):
        self.points[self.dates == dates] = points
        if dbhandle is not None:
            dbhandle.modify_measurements(self.ID, self.dates, self.points)

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


def main():
    from plot_cc import CCPlotter

    N = 100
    dates = np.linspace(0, 100, N)
    mn, st, unc = 10., 3., 10.
    points = (np.random.randn(N) * st) + mn
    cc = ControlChart(method_ID="NAVSZI_123", etalon_ID="BFG 9000",
                      paramname="TesztParaméter", dimension="m/s**2")
    cc.reference_from_stats(mn, st, unc)
    cc.add_points(dates, points)
    cc.report()

    plotter = CCPlotter(cc)
    plotter.plot()


if __name__ == '__main__':
    main()
