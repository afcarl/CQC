import os

cacheroot = os.path.expanduser("~/SciProjects/Project_CQC/")
emptyccimg = cacheroot + "emptycc.png"


def floatify(string):
    if string:
        return float(string.replace(",", "."))
    return None
