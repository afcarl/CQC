from tkinter import Tk

import numpy as np

from interface.ui_root import CCManagerRoot


def ccmanager_main():
    root = Tk()
    root = CCManagerRoot(root)
    root.mainloop()


def show_mpl_plot():
    from CQC.controlchart.chart import ControlChart
    from plotting.leveyjennings import LeveyJenningsChart

    N = 100
    dates = np.linspace(0, 100, N)
    mn, st, unc = 10., 3., 10.
    points = (np.random.randn(N) * st) + mn
    cc = ControlChart(mname="NAVSZI_123", rmat="BFG 9000",
                      pname="TesztParaméter", dim="m/s**2",
                      revision=0)
    cc.reference_from_stats(mn, st, unc)
    cc.add_points(dates, points)
    cc.report()

    plotter = LeveyJenningsChart(cc)
    # plotter.dump()
    plotter.plot()


if __name__ == '__main__':
    ccmanager_main()
