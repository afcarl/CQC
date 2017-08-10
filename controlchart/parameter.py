import abc

from tkinter import StringVar


class Parameter(abc.ABC):

    idfields = ("ID", "pID", "mID")
    methodfields = ("akkn", "methodname", "methodowner", "paramname", "dimension")
    ccfields = ("startdate", "refmaterial", "ccowner", "comment")
    statfields = ("refmean", "refstd", "uncertainty")
    fields = methodfields + ccfields + statfields

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

    def incorporate_values(self, data):
        invalid = [k for k in data if k not in self.fields]
        assert not invalid, "Invalid keywords: " + str(invalid)
        for k, v in data.items():
            self.dictionary[k].set(str(v))

    def __getitem__(self, item):
        if item not in self.dictionary:
            raise KeyError("No such param: " + str(item))
        return self.dictionary[item]

    def __setitem__(self, key, value):
        if key not in self.dictionary:
            raise KeyError("No such param: " + str(key))
        self.dictionary[key].set(value)

    def asvars(self, field=None):
        fields = {"method": self.methodfields, "cc": self.ccfields,
                  "stat": self.statfields, None: self.fields, "all": self.fields
                  }[field]
        return [self.dictionary[var] for var in fields]

    def asvals(self, field=None):
        return [str(var.get()) for var in self.asvars(field)]
