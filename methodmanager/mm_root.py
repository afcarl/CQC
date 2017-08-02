from tkinter import Tk, Frame, Label, Button
from tkinter.ttk import Treeview

from backend.dbconn import DBConnection
from backend.util import cacheroot


class MethodManagerRoot(Frame):

    def __init__(self, master: Tk, **kw):
        assert isinstance(master, Tk)
        super().__init__(master, **kw)

        self.master.title("Módszerkezelő modul")
        self.dbifc = DBConnection(dbpath=cacheroot + "TestDb.db",
                                  metapath=cacheroot + "meta.dat")
        self.twcols = ("modsz_azon", "akk_azon")

        Label(self, text="Az adatbázisban szereplő módszerek").pack()
        self.tw = None  # type: Treeview
        self.twmap = {}
        self.pack(fill="both", expand=True)
        self._build_listbox()

        Button(self, text="Új módszer felvétele...").pack(expand=True, fill="both")
        Button(self, text="Törlés").pack(expand=True, fill="both")
        Button(self, text="Megnyitás", width=7).pack(expand=True, fill="both")

    def _build_listbox(self):
        frame = Frame(self)
        tw = Treeview(frame, columns=self.twcols, height=20, selectmode="browse")
        mlb = "NAV SZI {}"
        for mID, method, mnum, akk in sorted(self.dbifc.get_methods(), key=lambda tup: tup[0]):
            idstr = mlb.format(mID)
            akkstr = mlb.format(akk) if akk else ""
            twmID = tw.insert("", "end", text=method, values=[idstr, akkstr])
            for pID, param, dim in self.dbifc.get_params(mID):
                twpID = tw.insert(twmID, "end", text=param, values=["", dim])
                self.twmap[twpID] = (twmID, mID, pID)

        tw.pack(fill="both", expand=True)
        frame.pack(fill="both", expand=True)
        self.tw = tw
