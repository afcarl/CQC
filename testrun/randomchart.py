import numpy as np

from CQC.backend.cchart import ControlChart
from CQC.backend.plot_cc import LeveyJenningsChart


dates = np.linspace(1, 100, 100)
testX = np.random.randn(*dates.shape) + 1.

cc = ControlChart("", "", "", "", 1)
cc.reference_from_stats(1., 1., 2.5)
cc.add_points(dates, testX)

LeveyJenningsChart(cc).plot()
