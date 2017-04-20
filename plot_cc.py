import numpy as np
from scipy import stats
from matplotlib import pyplot as plt


class CCPlotter(object):

    def __init__(self, cc):
        self.cc = cc
        self.ax = plt.gca()

    def _plot_hlines(self):

        def draw_stdline(parm):
            coef, col = parm
            plt.axhline(y=self.cc.refmean + coef * self.cc.refstd, xmin=datemin, xmax=datemax, color=col)

        datemin = np.min(self.cc.dates)
        datemax = np.max(self.cc.dates)
        plt.axhline(y=self.cc.refmean, xmin=datemin, xmax=datemax, color="green", linestyle="--")

        list(map(draw_stdline, ((1, "blue"), (-1, "blue"),
                                (2, "yellow"), (-2, "yellow"),
                                (3, "red"), (-3, "red"))))

    def _setup_axes(self):
        ax = plt.gca()
        ax.set_ylabel(self.cc.paramname)

        ax.set_axisbelow(True)
        ax.xaxis.grid(color="grey", linestyle="dashed")
        return ax

    def _add_zscore_axis(self, ax):
        zax = ax.twinx()
        zax.set_ylabel("Z-érték")
        lims = np.divide(np.subtract(ax.get_ylim(), self.cc.refmean), self.cc.refstd)
        zax.set_ylim(lims)

    def _scatter_points(self):
        Xs, Ys = np.array(self.cc.dates), np.array(self.cc.points)
        ywlim = self.cc.refmean - 1.9 * self.cc.refstd, self.cc.refmean + 1.9 * self.cc.refstd
        rdlim = self.cc.refmean - 2.9 * self.cc.refstd, self.cc.refmean + 2.9 * self.cc.refstd
        yargs = np.concatenate((np.argwhere((rdlim[0] < Ys) & (Ys < ywlim[0])),
                                np.argwhere((rdlim[1] > Ys) & (Ys > ywlim[1]))))
        rargs = np.concatenate((np.argwhere(Ys < rdlim[0]), np.argwhere(Ys > rdlim[1])))
        bargs = np.argwhere((ywlim[0] < Ys) & (Ys < ywlim[1]))

        plt.scatter(Xs[bargs], Ys[bargs], c="black", marker="o")
        plt.scatter(Xs[yargs], Ys[yargs], c="orange", marker="o")
        plt.scatter(Xs[rargs], Ys[rargs], c="red", marker="o")

    def _add_linear_trendline(self):
        z = np.polyfit(self.cc.dates, self.cc.points, 1)
        p = np.poly1d(z)
        r = stats.pearsonr(self.cc.points, p(self.cc.dates))[0] ** 2
        print("r^2 =", r)
        plt.plot(self.cc.dates, p(self.cc.dates), "r--", linewidth=3)

    def _set_titles(self):
        pt = "Kontroll diagram {} paraméterhez".format(self.cc.paramname)
        plt.title(pt)

    def plot(self):
        self._plot_hlines()
        ax = self._setup_axes()
        self._scatter_points()
        self._add_linear_trendline()
        self._add_zscore_axis(ax)
        plt.title("Kontroll diagram: " + self.cc.paramname)

        plt.show()

    def __call__(self):
        self.plot()
