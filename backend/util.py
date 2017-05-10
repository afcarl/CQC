from tkinter import StringVar

cacheroot = "/home/csa/SciProjects/Project_CQC/"
emptyccimg = cacheroot + "emptycc.png"


class CCParams:

    def __init__(self, mname=None, rmat=None, pname=None, dim=None,
                 revision=None, comment=None,
                 mean=None, std=None, uncertainty=None):

        self._paramnames = ("mname", "rmat", "pname", "dim", "revision", "comment",
                            "mean", "std", "uncertainty")
        self.__dict__.update({
            k: v for k, v in locals().items() if k != "self"
        })
        self.__dict__ = {
            k: (StringVar(value="") if v is None else v)
            for k, v in self.__dict__.items()
        }
        if not all(isinstance(v, StringVar) for k, v in self.__dict__.items()
                   if k[0] != "_"):
            raise ValueError("CCParams must be initialized with StringVar instances!")

    @classmethod
    def from_values(cls, header, stats):
        return cls(*[StringVar(val) for val in header] +
                    [StringVar(str(val).replace(".", ",")) for val in stats])

    @classmethod
    def from_ccobject(cls, ccobj):
        c = ccobj
        return cls.from_values(
            [c.method_ID, c.etalon_ID, c.paramname, c.dimension, c.revision, c.comment],
            [c.refmean, c.refstd, c.uncertainty]
        )

    def __getitem__(self, item):
        if item not in self.__dict__:
            raise KeyError("No such param: " + item)
        return self.__dict__[item]

    def __setitem__(self, key, value):
        if key not in self.__dict__:
            raise KeyError("No such param: ", + key)
        self.__dict__[key].set(value)

    def asvars(self):
        return tuple(self[pnm] for pnm in self._paramnames)

    def headervars(self):
        return self.asvars()[:6]

    def statvars(self):
        return self.asvars()[6:]

    def asvals(self):
        return [var.get() for var in self.headervars()] + \
               [floatify(var.get()) for var in self.statvars()]


def floatify(string):
    if string:
        return float(string.replace(",", "."))
    return None
