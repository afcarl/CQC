import numpy as np

from CQC.frontend.gui_root import Rootwin


def gui_main():
    root = Rootwin()
    root.mainloop()


def show_mpl_plot():
    from CQC.backend.cchart import ControlChart
    from CQC.backend.plot_cc import LeveyJenningsChart

    N = 100
    dates = np.linspace(0, 100, N)
    mn, st, unc = 10., 3., 10.
    points = (np.random.randn(N) * st) + mn
    cc = ControlChart(mname="NAVSZI_123", rmat="BFG 9000",
                      pname="TesztParaméter", dim="m/s**2")
    cc.reference_from_stats(mn, st, unc)
    cc.add_points(dates, points)
    cc.report()

    plotter = LeveyJenningsChart(cc)
    # plotter.dump()
    plotter.plot()


if __name__ == '__main__':
    gui_main()
