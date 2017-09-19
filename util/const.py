import os
from enum import IntEnum


class STAGE(IntEnum):
    method = 1
    param = 2
    cc = 3
    points = 4

cacheroot = os.path.expanduser("~/SciProjects/Project_CQC/")
defaults = cacheroot + "TestDb.db", cacheroot + "meta.dat"
noccimg = cacheroot + "nocc.png"
emptyccimg = cacheroot + "emptycc.png"
DBPATH = defaults[0]
METAPATH = defaults[1]

pkw = dict(fill="both", expand=True)
