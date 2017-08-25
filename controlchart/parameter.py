import abc
from tkinter import StringVar

from util import floatify


class _ParamData(abc.ABC):
    table = ""
    fields = ()

    def __init__(self, **kw):
        self.validate(kw)

        self.dictionary = {k: StringVar("") for k in self.fields}
        self.dictionary.update(kw)
        if "self" in kw:
            self.dictionary.pop("self")

        if not all(isinstance(v, StringVar) for v in self.dictionary.values()):
            raise ValueError("CCParams must be initialized with StringVar instances!")

        self.__dict__.update(self.dictionary)

    @classmethod
    def from_values(cls, data):
        return cls(**{k: StringVar(value=str(v)) for k, v in data.items()})

    @classmethod
    def from_database(cls, ID, dbifc):
        dbifc.x(f"SELECT * FROM {cls.table} WHERE id == ?;", [ID])
        obj = cls.from_values(dict(zip(cls.fields, dbifc.c.fetchone())))
        return obj

    def incorporate(self, data=None, **kw):
        self.validate(kw)
        for k, v in kw.items():
            self.__setitem__(k, v)
        if data is not None:
            self.incorporate(**data)

    def asvars(self):
        return [self.dictionary[var] for var in self.fields]

    def asvals(self):
        return [str(var.get()) for var in self.asvars()]

    def validate(self, data: dict):
        invalid = [k for k in data if k not in self.fields]
        if invalid:
            raise RuntimeError(f"Invalid keywords: {invalid}")

    def __getitem__(self, item):
        return self.dictionary[item].get()

    def __setitem__(self, key, value):
        self.dictionary[key].set(str(value))


class MethodData(_ParamData):
    table = "Method"
    fields = ("id", "staff_id", "name", "mnum", "akkn")


class ParameterData(_ParamData):
    table = "Parameter"
    fields = ("id", "method_id", "name", "dimension")


class CCData(_ParamData):
    table = "Control_chart"
    fields = ("id", "parameter_id", "staff_id", "startdate", "refmaterial",
              "comment", "refmean", "refstd", "uncertainty")
    statfields = ("refmean", "refstd", "uncertainty")

    def __getitem__(self, field):
        value = super().__getitem__(field)
        if field in self.statfields:
            value = floatify(value)
        return value

    def asvals(self):
        vals = super().asvals()
        vals[-3:] = map(float, vals[-3:])
        return vals


# noinspection PyMissingConstructor
class Measurements(_ParamData):
    fields = ("id", "cc_id", "staff_id", "reference", "comment", "date", "value")
    table = "Control_measurement"

    def __init__(self, **kw):
        self.validate(kw)
        self.dictionary = {k: [] for k in self.fields}
        self.dictionary.update(kw)

    @classmethod
    def from_database(cls, ccID, dbifc):
        select = f"SELECT {', '.join(cls.fields)} FROM {cls.table} WHERE cc_ID == ?;"
        dbifc.x(select, [ccID])
        data_transposed = map(list, zip(*dbifc.c.fetchall()))
        return cls(**dict(zip(cls.fields, data_transposed)))

    @classmethod
    def from_values(cls, data):
        return cls(**data)

    def asvars(self):
        raise NotImplementedError

    def __getitem__(self, item):
        return self.dictionary[item]

    def __setitem__(self, key, value):
        self.dictionary[key] = value


class Parameter:

    def __init__(self, mdata=None, pdata=None, ccdata=None):
        self.mdata = MethodData() if mdata is None else mdata
        self.pdata = ParameterData() if pdata is None else pdata
        self.ccdata = CCData() if ccdata is None else ccdata

    @classmethod
    def populate(cls, ccID, dbifc):
        ccd = CCData.from_database(ccID, dbifc)
        pd = ParameterData.from_database(ccd["parameter_id"], dbifc)
        md = MethodData.from_database(pd["method_id"], dbifc)
        return cls(md, pd, ccd)
