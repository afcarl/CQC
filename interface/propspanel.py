from tkinter import Frame, Button

from .recordframe import MethodFrame, ParamFrame, CCFrame
from controlchart import ControlChart
from util import pkw

pcfg = dict(bd=4, relief="raised")


class PropertiesPanel(Frame):

    stages = ("method", "param", "cc")

    def __init__(self, master, ccobj: ControlChart, dbifc, **kw):
        super().__init__(master, **kw)
        self.ccobj = ccobj
        self.frames = {
            "method": MethodFrame(self, dbifc, resultobj=ccobj.mrec),
            "param": ParamFrame(self, dbifc, resultobj=ccobj.prec),
            "cc": CCFrame(self, dbifc, resultobj=ccobj.ccrec)
        }
        for stage in self.stages:
            self.frames[stage].pack()
        self.okbutton = Button(self, text="Kész", state="disabled", command=self.okcommand)
        self.okbutton.pack(**pkw)
        self.lock()

    def okcommand(self):
        for fname in self.stages:
            rec = self.frames[fname].check()
            if rec is None:
                return
            self.ccobj.rec[fname] = rec

    def lock(self):
        for w in self.frames.values():
            w.lock()
        self.okbutton.configure(state="disabled")

    def unlock(self, until=None):
        self.lock()
        for stage in self.stages[::-1]:
            self.frames[stage].unlock()
            if stage == until:
                break
        self.okbutton.configure(state="active")

    @property
    def type(self):
        return self.__class__.__name__
