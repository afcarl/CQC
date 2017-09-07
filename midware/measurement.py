from midware.parameter import RecordBase
from util import repeat


# noinspection PyMissingConstructor,PyMethodOverriding
class Measurements(RecordBase):
    table = "Control_measurement"
    fields = ("id", "cc_id", "staff_id", "reference", "comment", "date", "value")
    upstream_key = "cc_id"

    def __init__(self, globref=False):
        self.globref = globref
        self.data = {k: [] for k in self.fields}

    def incorporate(self, data):
        self.validate(data)
        for key, value in data.items():
            assert isinstance(value, list)
            self.data[key].extend(value)
        self.saved = False

    def setall(self, **kw):
        assert not all(p is None for p in locals().values())
        N = len(self.data["value"])
        if not N:
            return
        if kw.get("reference", None) is None:
            kw["reference"] = self.globref
        self.incorporate(repeat(N, **kw))

    def asmatrix(self, transpose=True):
        mydata = [self.data[field] for field in self.fields[1:]]
        return list(map(list, zip(*mydata))) if transpose else mydata

    @classmethod
    def from_database(cls, ccID, dbifc, reference):
        select = " ".join((
            f"SELECT {', '.join(cls.fields)} FROM {cls.table}",
            f" WHERE cc_ID == ? AND",
            "reference;" if reference else "NOT reference;"
        ))
        dbifc.x(select, [ccID])
        data_transposed = map(list, zip(*dbifc.c.fetchall()))
        obj = cls()
        obj.incorporate(dict(zip(cls.fields, data_transposed)))
        obj.saved = True
        return obj

    def stats(self):
        assert self.globref, "Why would you calc stats on non-reference measurements?"
        from statistics import mean, stdev
        return mean(self.data["value"]), stdev(self.data["value"])
