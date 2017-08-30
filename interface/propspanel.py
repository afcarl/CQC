from tkinter import Toplevel, Button

from .recordframe import MethodFrame, ParamFrame, CCFrame
from controlchart import ControlChart
from util import pkw

pcfg = dict(bd=4, relief="raised")


class PropertiesPanel(Toplevel):

    stages = ("method", "param", "cc")

    def __init__(self, master, ccobj: ControlChart, dbifc, stage=None, **kw):
        super().__init__(master, **kw)
        self.title("Kontroll diagram tulajdonságok")
        self.transient(master)

        self.stage = stage
        self.ccobj = ccobj
        self.frames = {
            "method": MethodFrame(self, dbifc, resultobj=ccobj.mrec),
            "param": ParamFrame(self, dbifc, resultobj=ccobj.prec),
            "cc": CCFrame(self, dbifc, resultobj=ccobj.ccrec)
        }
        for s in self.stages:
            self.frames[s].pack()
        if stage:
            self.botbut = Button(self, text="Kész", state="active", command=self.okcommand)
        else:
            self.botbut = Button(self, text="Szerkesztés", state="active", command=self.editcommand)
        self.botbut.pack(**pkw)
        self.lock()
        self.unlock()

    def editcommand(self):
        self.stage = "cc"
        self.unlock()
        self.botbut.destroy()
        self.botbut = Button(self, text="Kész", state="active", command=self.okcommand)
        self.botbut.pack(**pkw)

    def okcommand(self):
        for fname in self.stages[::-1]:
            rec = self.frames[fname].check()
            if rec is None:
                return
            if fname == self.stage:
                break
        self.destroy()

    def lock(self):
        for w in self.frames.values():
            w.lock()

    def unlock(self):
        if self.stage is None:
            return
        self.lock()
        for stage in self.stages[::-1]:
            self.frames[stage].unlock()
            if stage == self.stage:
                break

    @property
    def type(self):
        return self.__class__.__name__
