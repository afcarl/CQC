from .parameter import Parameter, Measurements
from plotting import LeveyJenningsChart
from util import cacheroot


class ControlChart(object):

    def __init__(self, param: Parameter, measurements: Measurements):
        self.measure = measurements
        self.param = param

    @classmethod
    def from_database(cls, dbifc, ccID):
        param = Parameter.populate(ccID, dbifc)
        measurements = Measurements.from_database(ccID, dbifc)
        return cls(param, measurements)

    @staticmethod
    def load(path=None):
        import pickle
        import gzip
        if path is None:
            path = cacheroot + "cchart.pkl.gz"
        with gzip.open(path, "rb") as handle:
            cc = pickle.load(handle)
        return cc

    def plot(self, show=False):
        if not self.plottable:
            raise RuntimeError("Not plottable!")
        plotter = LeveyJenningsChart(self.param, self.measure["value"])
        dumppath = cacheroot + "cc_pic.png"
        plotter.plot(show=show, dumppath=dumppath)
        return dumppath

    def backup(self, path=None):
        import pickle
        import gzip
        if self.param.ccdata["id"] is None:
            print("Not backing up new ControlChart!")
            return
        flnm = f"KD-{self.param.ccdata['id']}.pkl.gz"
        if path is None:
            path = cacheroot
        with gzip.open(path + flnm, "wb") as handle:
            pickle.dump(self, handle)
        return path

    def add_points(self, data, reference=False):
        N = len(data)
        self.measure.incorporate(dict(
            cc_id=[self.ID for _ in range(N)],
            staff_id=[self.param.ccdata["staff_id"] for _ in range(N)],
            reference=[reference for _ in range(N)], **data
        ))

    @property
    def values(self):
        return self.measure["value"]

    @property
    def dates(self):
        return self.measure["date"]

    @property
    def ID(self):
        return self.param.ccdata["id"]

    @property
    def plottable(self):
        return len(self.measure["value"]) > 0
