import getpass
from datetime import datetime

from backend.util import cacheroot


def log(*args, flpath=None, sep=" ", end="\n", echo=False):
    flpath = cacheroot+"sys.log" if flpath is None else flpath
    prfx = datetime.now().strftime("%Y.%m.%d %H:%M:%S -- ")
    mdfx = sep.join(args)
    psfx = " -- " + getpass.getuser() + end
    if echo:
        print(mdfx)
    with open(flpath, "a") as handle:
        handle.write(" -- ".join((prfx, mdfx, psfx)))