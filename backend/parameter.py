import abc

from tkinter import StringVar


class _Parameter(abc.ABC):

    type = ""
    fields = ()

    def __init__(self, **kw):

        invalid = [k for k in kw if k not in self.fields]
        if invalid:
            raise RuntimeError("Wrong keyword arguments: " + str(invalid))

        self.dictionary = {}
        self.dictionary.update(kw)
        if "self" in kw:
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
        return cls.from_values({k: ccobj.__dict__[k] for k in cls.fields})

    def __getitem__(self, item):
        if item not in self.dictionary:
            raise KeyError("No such param: " + str(item))
        return self.dictionary[item]

    def __setitem__(self, key, value):
        if key not in self.dictionary:
            raise KeyError("No such param: " + str(key))
        self.dictionary[key].set(value)

    def asvars(self):
        return [self.dictionary[var] for var in self.fields]

    def asvals(self):
        return [str(var.get()) for var in self.asvars()]


class MethodParameter(_Parameter):

    type = "methodparameter"
    fields = ("methodnum", "method", "methodowner", "paramname", "dimension")


class CCParameter(_Parameter):
    
    type = "ccparameter"
    fields = ("startdate", "refmaterial", "ccowner", "comment")


class StatParameter(_Parameter):

    type = "statparameter"
    fields = ("refmean", "refstd", "uncertainty")

    def asvals(self):
        return [float(var.get().replace(",", ".")) for var in self.asvars()]


class AllParameter(_Parameter):

    type = "allparameter"
    fields = MethodParameter.fields + CCParameter.fields + StatParameter.fields

    def __init__(self, methodparam: MethodParameter,
                 ccparam: CCParameter,
                 statparam: StatParameter):
        super().__init__(
            **dict(zip(methodparam.fields, methodparam.asvars())),
            **dict(zip(ccparam.fields, ccparam.asvars())),
            **dict(zip(statparam.fields, statparam.asvars()))
        )
