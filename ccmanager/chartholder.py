from tkinter import Frame, Label, IntVar, Scale, PhotoImage

from backend.cchart import ControlChart
from backend.util import emptyccimg


class ChartHolder(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.ccobject = None
        self.ccimg = None
        self.canvas = Label(self)
        self.canvas.pack()
        self.scalevar = IntVar(value=30)
        self.scale = Scale(
            self, from_=1, to=100, variable=self.scalevar,
            orient="horizontal", showvalue=False,
            sliderlength=100, digits=0, command=self.movescale
        )
        self.scale.pack(fill="both", expand=1)

    def movescale(self, n):
        print("movescale called with n =", n)

    def new_ccobject(self, args):
        self.ccobject = ControlChart(*args)
        self.update_image()

    def set_ccobject(self, ccobj):
        self.ccobject = ccobj
        self.update_image()

    def update_image(self):
        if self.ccobject is None:
            self.ccimg = PhotoImage(file=emptyccimg)
        else:
            self.ccimg = PhotoImage(file=self.ccobject.plot())
        self.canvas.config(image=self.ccimg)
