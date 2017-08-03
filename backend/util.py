import os

cacheroot = os.path.expanduser("~/SciProjects/Project_CQC/")
defaults = cacheroot + "TestDb.db", cacheroot + "meta.dat"
DBPATH, METAPATH = defaults
emptyccimg = cacheroot + "emptycc.png"


def floatify(string):
    if string:
        return float(string.replace(",", "."))
    return None
