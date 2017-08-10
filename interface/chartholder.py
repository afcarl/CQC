from tkinter import Frame, Label, PhotoImage

from util.const import emptyccimg


class ChartHolder(Frame):

    def __init__(self, master, ccobj=None, **kw):
        super().__init__(master, **kw)
        self.ccobject = ccobj
        self.ccimg = None
        self.canvas = Label(self)
        self.canvas.pack()

    def set_ccobject(self, ccobj):
        self.ccobject = ccobj
        self.update_image()

    def update_image(self):
        if self.ccobject is None or not self.ccobject.plottable:
            self.ccimg = PhotoImage(file=emptyccimg)
        else:
            self.ccimg = PhotoImage(file=self.ccobject.plot())
        self.canvas.config(image=self.ccimg)
