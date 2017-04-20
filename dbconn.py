import sqlite3 as sql


class MetaHandler(object):

    @staticmethod
    def read(path):
        with open(path) as fileobj:
            data = fileobj.read()
        lines = data.split("\n")
        mapping = {k: v for k, v in [line.split(": ") for line in lines if line]}
        return mapping


# noinspection PyUnresolvedReferences
class DBConnection(object):

    def __init__(self, dbpath, metapath):
        self.__dict__.update(MetaHandler.read(metapath))
        self.__dict__.update({k: v for k, v in locals().items() if k != "self"})
        self.methods = []

    @property
    def cursor(self):
        conn = sql.connect(self.dbpath)
        cur = conn.cursor()
        return cur

    def newmethod(self, methodobj):
        self.methods.append(methodobj)
