from datetime import datetime

from .cchart import ControlChart


def instantiate_cc(data):
    now = datetime.now().strftime("%Y.%m.%d")
    mname, rmat, pname, dim, rmean, rstd, unc = data
    cc = ControlChart(mname, rmat, pname, dim, 1, now)
    cc.reference_from_stats(rmean, rstd, unc)
    cc.plot()
    return cc
