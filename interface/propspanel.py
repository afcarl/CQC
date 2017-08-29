from tkinter import Frame

from .recordframe import MethodFrame, ParamFrame, CCFrame
from controlchart import ControlChart
from util import globvars

pkw = dict(fill="both", expand=True)
pcfg = dict(bd=4, relief="raised")


class PropertiesPanel(Frame):

    stages = ("method", "param", "cc")

    def __init__(self, master, ccobj: ControlChart, **kw):
        super().__init__(master, **kw)
        self.ccobj = ccobj
        dbifc = globvars.logical_root.dbifc
        self.frames = {
            "method": MethodFrame(self, dbifc, resultobj=ccobj.mrec),
            "param": ParamFrame(self, dbifc, resultobj=ccobj.prec),
            "cc": CCFrame(self, dbifc, resultobj=ccobj.ccrec)
        }
        for stage in self.stages:
            self.frames[stage].pack()
        self.lock()

    def lock(self):
        for w in self.frames.values():
            w.lock()

    def unlock(self, until=None):
        self.lock()
        for stage in self.stages[::-1]:
            self.frames[stage].unlock()
            if stage == until:
                break

    @property
    def type(self):
        return self.__class__.__name__
