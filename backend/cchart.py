import numpy as np

from .plot_cc import LeveyJenningsChart
from .util import cacheroot
from .parameter import CCParam


class ControlChart(object):

    def __init__(self, ccparam: CCParam, ID=None, points=None):
        assert isinstance(ccparam, CCParam)
        self.ID = ID
        self.pointsdata = None if points is None else np.array(points)
        self.points = np.array([]) if points is None else self.pointsdata[:, 2].astype(float)
        self.__dict__.update(dict(zip(ccparam.paramnames, ccparam.asvals())))
        pass

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
        plotter = LeveyJenningsChart(self)
        dumppath = cacheroot + "cc_pic.png"
        plotter.plot(show=show, dumppath=dumppath)
        return dumppath

    def backup(self, path=None):
        import pickle
        import gzip
        if self.ID is None:
            print("Not backing new ControlChart!")
            return
        flnm = f"KD-{self.ID}.pkl.gz"
        if path is None:
            path = cacheroot
        with gzip.open(path + flnm, "wb") as handle:
            pickle.dump(self, handle)
        return path

    @property
    def plottable(self):
        return len(self.points) > 5
