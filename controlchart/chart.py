from .parameter import MethodRecord, ParameterRecord, CCRecord, Measurements
from plotting import LeveyJenningsChart
from util import cacheroot, dumpobj, loadobj


class ControlChart:

    def __init__(self, mrec=None, prec=None, ccrec=None, meas=None, refmeas=None):
        self.mrec = MethodRecord() if mrec is None else mrec
        self.prec = ParameterRecord() if prec is None else prec
        self.ccrec = CCRecord() if ccrec is None else ccrec
        self.meas = Measurements() if meas is None else meas
        self.refmeas = Measurements() if refmeas else None

    @classmethod
    def from_database(cls, ccID, dbifc):
        ccd = CCRecord.from_database(ccID, dbifc)
        pd = ParameterRecord.from_database(ccd["parameter_id"], dbifc)
        md = MethodRecord.from_database(pd["method_id"], dbifc)
        meas = Measurements.from_database(ccID, dbifc, reference=False)
        ref = Measurements.from_database(ccID, dbifc, reference=True)
        return cls(md, pd, ccd, meas, ref)

    @staticmethod
    def pklload(path=None):
        if path is None:
            path = cacheroot + "cchart.pkl.gz"
        return loadobj(path)

    def pkldump(self, path=None):
        if self.ccrec["id"] is None:
            print("Not backing up new ControlChart!")
            return
        flnm = f"KD-{self.ccrec['id']}.pkl.gz"
        if path is None:
            path = cacheroot
        dumpobj(self, flnm)
        return path

    def plot(self, show=False):
        if not self.plottable:
            raise RuntimeError("Not plottable!")
        plotter = LeveyJenningsChart(self)
        dumppath = cacheroot + "cc_pic.png"
        plotter.plot(show=show, dumppath=dumppath)
        return dumppath

    def add_points(self, data, reference=False):
        N = len(data)
        self.meas.incorporate(dict(
            cc_id=[self.ID for _ in range(N)],
            staff_id=[self.ccrec["staff_id"] for _ in range(N)],
            reference=[reference for _ in range(N)], **data
        ))

    @property
    def ID(self):
        return self.ccrec["id"]

    @property
    def plottable(self):
        return len(self.meas["value"]) > 0
