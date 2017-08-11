from tkinter import StringVar

from util import floatify


class _ParamData:
    type = ""
    table = ""
    fields = ()

    def __init__(self, **kw):
        invalid = [k for k in kw if k not in self.fields]
        if invalid:
            raise RuntimeError("Wrong keyword arguments: " + str(invalid))

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

    def incorporate_values(self, data=None, **kw):
        invalid = [k for k in kw if k not in self.fields]
        if data is not None:
            invalid += [k for k in data if k not in self.fields]
        assert not invalid, "Invalid keywords: " + str(invalid)
        for k, v in kw.items():
            self.dictionary[k].set(str(v))
        if data is not None:
            for k, v in data.items():
                self.dictionary[k].set(str(v))

    def asvars(self):
        return [self.dictionary[var] for var in self.fields]

    def asvals(self):
        return [str(var.get()) for var in self.asvars()]

    def __getitem__(self, item):
        if item not in self.dictionary:
            raise KeyError("No such param: " + str(item))
        return self.dictionary[item].get()

    def __setitem__(self, key, value):
        if key not in self.dictionary:
            raise KeyError("No such param: " + str(key))
        self.dictionary[key].set(str(value))


class MethodData(_ParamData):
    type = "methoddata"
    table = "Method"
    fields = ("id", "staff_id", "name", "mnum", "akkn")


class ParameterData(_ParamData):
    type = "parameterdata"
    table = "Parameter"
    fields = ("id", "method_id", "name", "dimension")


class CCData(_ParamData):
    type = "ccdata"
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
