from tkinter import Frame

from util import pkw


class RootMainFrame(Frame):

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._active_panel = None

    def switch(self):
        self.activate(
            "ChartHolder" if self._active_panel.type == "PropertiesPanel" else "PropertiesPanel"
        )

    def activate(self, what):
        if self._active_panel is not None:
            if self._active_panel.type == what:
                return
            self._active_panel.pack_forget()
        self._active_panel = {"ChartHolder": self.master.chartholder,
                              "PropertiesPanel": self.master.propspanel}[what]
        self._active_panel.pack(**pkw)
