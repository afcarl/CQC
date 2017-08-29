from tkinter import Frame

from .recordframe import MethodFrame, ParamFrame, CCFrame
from controlchart import ControlChart
from util import globvars

pkw = dict(fill="both", expand=True)
pcfg = dict(bd=4, relief="raised")


class PropertiesPanel(Frame):

    def __init__(self, master, ccobj: ControlChart, **kw):
        super().__init__(master, **kw)
        self.ccobj = ccobj
        dbifc = globvars.logical_root.dbifc
        self.frames = {
            "method": MethodFrame(self, dbifc, resultobj=ccobj.mrec),
            "param": ParamFrame(self, dbifc, resultobj=ccobj.prec),
            "cc": CCFrame(self, dbifc, resultobj=ccobj.ccrec)
        }
        for f in self.frames.values():
            f.pack()

        self.lock()

    def lock(self):
        for w in self.frames.values():
            w.lock()

    def unlock(self):
        for w in self.frames.values():
            w.lock()
