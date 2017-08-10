import abc

from tkinter import StringVar


class Parameter(abc.ABC):

    ccfields = ("id", "startdate", "refmaterial", "refmean", "refstd",
                "uncertainty", "comment", "parameter_id", "allomany_id")
    paramfields = ("id", "paramname", "dimension", "modszer_id")
    methodfields = ("id", "methodname", "mnum", "akkn", "allomany_id")

    statfields = ("refmean", "refstd", "uncertainty")
    idfields = ("id", "modszer_id", "parameter_id", "allomany_id")

    fields = ccfields + paramfields + methodfields

    def __init__(self, **kw):

        invalid = [k for k in kw if k not in self.fields]
        if invalid:
            raise RuntimeError("Wrong keyword arguments: " + str(invalid))

        self.dictionary = {k: StringVar("") for k in self.fields}
        self.dictionary.update(kw)
        if "self" in kw:
            self.dictionary.pop("self")
        if not all(isinstance(v, StringVar) for k, v in self.dictionary.items()
                   if k[0] != "_"):
            raise ValueError("CCParams must be initialized with StringVar instances!")
        assert all(field in self.dictionary for field in self.fields)

    @classmethod
    def from_values(cls, data):
        return cls(**{k: StringVar(value=str(v)) for k, v in data.items()})

    @classmethod
    def from_ccobject(cls, ccobj):
        return cls.from_values({k: ccobj.__dict__[k] for k in cls.fields})

    @classmethod
    def from_database(cls, ccID, dbifc):
        selectbase = "SELECT {} FROM {} WHERE id == ?;"
        par = cls()
        dbifc.x(selectbase.format(", ".join(cls.ccfields), "Kontroll_diagram"), [ccID])
        par.incorporate_values(dict(zip(cls.ccfields, dbifc.c.fetchone())))
        dbifc.x(selectbase.format(", ".join(cls.paramfields), "Parameter"), [par["parameter_id"]])
        par.incorporate_values(dict(zip(cls.paramfields, dbifc.c.fetchone())))
        dbifc.x(selectbase.format(", ".join(cls.methodfields), "Modszer"), [par["method_id"]])
        par.incorporate_values(dict(zip(cls.paramfields, dbifc.c.fetchone())))
        par["method_id"] = par["id"]
        par["id"] = ccID
        return par

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

    def __getitem__(self, item):
        if item not in self.dictionary:
            raise KeyError("No such param: " + str(item))
        return self.dictionary[item].get()

    def __setitem__(self, key, value):
        if key not in self.dictionary:
            raise KeyError("No such param: " + str(key))
        self.dictionary[key].set(value)

    def asvars(self, field=None):
        fields = {"method": self.methodfields, "cc": self.ccfields, "id": self.idfields,
                  "stat": self.statfields, None: self.fields, "all": self.fields
                  }[field]
        return [self.dictionary[var] for var in fields]

    def asvals(self, field=None):
        return [str(var.get()) for var in self.asvars(field)]
