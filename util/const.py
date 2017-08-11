import os

cacheroot = os.path.expanduser("~/SciProjects/Project_CQC/")
defaults = cacheroot + "TestDb.db", cacheroot + "meta.dat"
emptyccimg = cacheroot + "emptycc.png"
DBPATH = defaults[0]
METAPATH = defaults[1]

pkw = dict(fill="both", expand=True)
