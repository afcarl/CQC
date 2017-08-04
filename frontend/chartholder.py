from tkinter import Frame, Label, IntVar, Scale, PhotoImage

from backend.util import emptyccimg


class ChartHolder(Frame):

    def __init__(self, master, ccobj=None, **kw):
        super().__init__(master, **kw)
        self.ccobject = ccobj
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

    def set_ccobject(self, ccobj):
        self.ccobject = ccobj
        self.update_image()

    def update_image(self):
        if self.ccobject is None or not self.ccobject.plottable:
            self.ccimg = PhotoImage(file=emptyccimg)
        else:
            self.ccimg = PhotoImage(file=self.ccobject.plot())
        self.canvas.config(image=self.ccimg)
