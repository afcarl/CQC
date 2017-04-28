from CQC.backend.cchart import ControlChart
from CQC.backend.plot_cc import PlotBuilder


def create_empty_cchart(dumppath):
    import numpy as np

    dates = np.linspace(1, 100, 4)
    points = np.ones_like(dates)
    cc = ControlChart("?", "?", "?", "?", 1)
    cc.reference_from_stats(0, 1, 2)
    cc.add_points(dates, points)
    pb = PlotBuilder(cc)
    pb.dump(dumppath)


if __name__ == '__main__':
    create_empty_cchart("/home/csa/SciProjects/Project_CQC/emptycc.png")