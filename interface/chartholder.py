from tkinter import Frame, Label, PhotoImage

from util.const import emptyccimg


class ChartHolder(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.ccimg = None
        self.canvas = Label(self)
        self.canvas.pack()

    def update_image(self, ccobject=None):
        if ccobject is None or not ccobject.plottable:
            self.ccimg = PhotoImage(file=emptyccimg)
        else:
            self.ccimg = PhotoImage(file=ccobject.plot())
        self.canvas.config(image=self.ccimg)
