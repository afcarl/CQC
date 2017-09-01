from util import repeat


class _Record:
    table = ""
    fields = ()
    upstream_key = None

    def __init__(self):
        self.data = {k: None for k in self.fields}
        self.saved = True

    @classmethod
    def from_database(cls, ID, dbifc):
        dbifc.x(f"SELECT * FROM {cls.table} WHERE id == ?;", [ID])
        obj = cls()
        obj.incorporate(dict(zip(cls.fields, dbifc.c.fetchone())))
        obj.saved = True
        return obj

    def incorporate(self, data=None, **kw):
        for k, v in kw.items():
            self.__setitem__(k, v)
        if data is not None:
            self.incorporate(**data)

    def asvals(self):
        return [self.data[d] for d in self.fields]

    def validate(self, data: dict):
        invalid = [k for k in data if k not in self.fields]
        if invalid:
            raise RuntimeError(f"Invalid keywords: {invalid}")

    @property
    def upstream_id(self):
        return self[self.upstream_key]

    @property
    def isnew(self):
        return self.data["id"] is None

    @upstream_id.setter
    def upstream_id(self, value):
        self[self.upstream_key] = value

    def __getitem__(self, item):
        if item is None:
            return None
        return self.data[item]

    def __setitem__(self, key, value):
        if key not in self.data:
            raise KeyError(f"No such field: {key}")
        if self.data[key] == value:
            return
        self.data[key] = value
        self.saved = False


class MethodRecord(_Record):
    table = "Method"
    fields = ("id", "staff_id", "name", "mnum", "akkn")
    upstream_key = None


class ParameterRecord(_Record):
    table = "Parameter"
    fields = ("id", "method_id", "name", "dimension")
    upstream_key = "method_id"


class CCRecord(_Record):
    table = "Control_chart"
    fields = ("id", "parameter_id", "staff_id", "startdate", "refmaterial",
              "comment", "refmean", "refstd", "uncertainty")
    statfields = ("refmean", "refstd", "uncertainty")
    upstream_key = "parameter_id"


# noinspection PyMissingConstructor,PyMethodOverriding
class Measurements(_Record):
    table = "Control_measurement"
    fields = ("id", "cc_id", "staff_id", "reference", "comment", "date", "value")
    upstream_key = "cc_id"

    def __init__(self, globref=False):
        self.globref = globref
        self.data = {k: [] for k in self.fields}

    def extend(self, data):
        self.validate(data)
        for key, value in data.items():
            assert isinstance(value, list)
            self.data[key].extend(value)
        self.saved = False

    def setall(self, **kw):
        assert not all(p is None for p in locals().values())
        N = len(self.data["value"])
        assert N
        if kw.pop("reference", None) is None:
            reference = self.globref
        self.extend(repeat(N, **kw))

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
        obj.extend(dict(zip(cls.fields, data_transposed)))
        obj.saved = True
        return obj

    def stats(self):
        assert self.globref, "Why would you calc stats on non-reference measurements?"
        from statistics import mean, stdev
        return mean(self.data["value"]), stdev(self.data["value"])
