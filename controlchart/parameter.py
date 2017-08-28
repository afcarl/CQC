from tkinter import StringVar

from util import floatify


class _Record:
    table = ""
    fields = ()

    def __init__(self, **kw):
        self.validate(kw)
        self.data = {k: StringVar("") for k in self.fields}
        self.data.update(kw)
        if "self" in kw:
            self.data.pop("self")

        if not all(isinstance(v, StringVar) for v in self.data.values()):
            raise ValueError("_ParamData must be initialized with StringVar instances!")

        self.__dict__.update(self.data)

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
        return [self.data[var] for var in self.fields]

    def asvals(self):
        return [str(var.get()) for var in self.asvars()]

    def validate(self, data: dict):
        invalid = [k for k in data if k not in self.fields]
        if invalid:
            raise RuntimeError(f"Invalid keywords: {invalid}")

    def __getitem__(self, item):
        return self.data[item].get()

    def __setitem__(self, key, value):
        self.data[key].set(str(value))


class MethodRecord(_Record):
    table = "Method"
    fields = ("id", "staff_id", "name", "mnum", "akkn")


class ParameterRecord(_Record):
    table = "Parameter"
    fields = ("id", "method_id", "name", "dimension")


class CCRecord(_Record):
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


# noinspection PyMissingConstructor,PyMethodOverriding
class Measurements(_Record):
    fields = ("id", "cc_id", "staff_id", "reference", "comment", "date", "value")
    table = "Control_measurement"

    def __init__(self, globref=False, **kw):
        self.validate(kw)
        self.globref = globref
        self.dictionary = {k: [] for k in self.fields}
        self.dictionary.update(kw)

    @classmethod
    def from_database(cls, ccID, dbifc, reference):
        select = " ".join((
            f"SELECT {', '.join(cls.fields)} FROM {cls.table}",
            f" WHERE cc_ID == ? AND",
            "reference;" if reference else "NOT reference;"
        ))
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
