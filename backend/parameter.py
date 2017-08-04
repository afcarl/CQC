from tkinter import StringVar


class CCParam:

    paramnames = ("startdate", "refmaterial", "refmean", "refstd", "uncertainty",
                  "paramname", "dimension", "owner", "comment")
    stats = ("refmean", "refstd", "uncertainty")

    def __init__(self, startdate=None, refmaterial=None,
                 refmean=None, refstd=None, uncertainty=None,
                 comment=None, paramname=None, dimension=None, owner=None):

        self.dictionary = {}
        self.dictionary.update(locals())
        self.dictionary.pop("self")
        self.dictionary = {
            k: (StringVar(value="") if v is None else v)
            for k, v in self.dictionary.items()
        }
        if not all(isinstance(v, StringVar) for k, v in self.dictionary.items()
                   if k[0] != "_"):
            raise ValueError("CCParams must be initialized with StringVar instances!")

    @classmethod
    def from_values(cls, data):
        return cls(**{k: StringVar(value=str(v)) for k, v in data.items()})

    @classmethod
    def from_ccobject(cls, ccobj):
        return cls.from_values({k: ccobj.__dict__[k] for k in cls.paramnames})

    def __getitem__(self, item):
        if item not in self.dictionary:
            raise KeyError("No such param: " + str(item))
        return self.dictionary[item]

    def __setitem__(self, key, value):
        if key not in self.dictionary:
            raise KeyError("No such param: " + str(key))
        self.dictionary[key].set(value)

    def asvars(self):
        return [self.dictionary[var] for var in self.paramnames]

    def asvals(self):
        return [float(var.get()) if k in self.stats else str(var.get())
                for k, var in zip(self.paramnames, self.asvars())]
