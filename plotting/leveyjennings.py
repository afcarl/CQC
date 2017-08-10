import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

from util import floatify


class LeveyJenningsChart(object):

    ax = plt.gca()
    Xs = None

    def __init__(self, param, points):
        self.refmean = floatify(param["refmean"])
        self.refstd = floatify(param["refstd"])
        self.uncertainty = floatify(param["uncertainty"])
        self.param = param
        self.points = points

    def _plot_hlines(self):

        def draw_dual(coef, col):
            plt.axhline(y=self.refmean + coef * self.refstd, color=col)
            plt.axhline(y=self.refmean - coef * self.refstd, color=col)
            pass

        m, s, u = self.refmean, self.refstd, self.uncertainty
        plt.axhline(y=m, color="purple", linestyle="--")
        for num, color in zip((2*s, 3*s, u), ("blue", "red", "green")):
            draw_dual(num, color)

    def _setup_axes(self):
        ax = plt.gca()
        ax.set_ylabel(self.param["paramname"].get())

        ax.set_axisbelow(True)
        ax.xaxis.grid(color="grey", linestyle="dashed")
        return ax

    def _add_zscore_axis(self, ax):
        zax = ax.twinx()
        zax.set_ylabel("Z-érték")
        lims = np.divide(np.subtract(ax.get_ylim(), self.refmean), self.refstd)
        zax.set_ylim(lims)
        zax.set_yticklabels(abs(i) for i, item in enumerate(ax.get_yticklabels(), start=-4))

    def _scatter_points(self, annot):

        def annotate(arg):
            date, point = arg
            z = (point - self.refmean) / self.refstd
            z = round(z, 2)
            va = "top" if z < 0 else "bottom"
            z = abs(z)
            tx = "{} {}\nZ° = {}".format(round(point, 4), self.param["dimension"].get(), z)
            # offsx = 10. if point > self.cc.refmean else -10.
            # offsy = 20. if date > np.mean(self.cc.dates) else -10.
            self.ax.annotate(tx, xy=(date, point), xycoords="data",
                             horizontalalignment="right", verticalalignment=va)

        Ys = np.array(self.points)
        Xs = np.arange(1, len(Ys)+1)
        ywlim = self.refmean - 1.95 * self.refstd, self.refmean + 1.95 * self.refstd
        rdlim = self.refmean - 2.95 * self.refstd, self.refmean + 2.95 * self.refstd
        yargs = np.concatenate((np.argwhere((rdlim[0] < Ys) & (Ys < ywlim[0])),
                                np.argwhere((rdlim[1] > Ys) & (Ys > ywlim[1])))).ravel()
        rargs = np.concatenate((np.argwhere(Ys < rdlim[0]), np.argwhere(Ys > rdlim[1]))).ravel()
        bargs = np.argwhere((ywlim[0] < Ys) & (Ys < ywlim[1])).ravel()

        plt.scatter(Xs[bargs], Ys[bargs], c="black", marker=".")
        plt.plot(Xs, Ys, "b-", linewidth=1)
        if len(yargs):
            plt.scatter(Xs[yargs], Ys[yargs], c="orange", marker=".")
            if annot:
                list(map(annotate, zip(Xs[yargs], Ys[yargs])))
        if len(rargs):
            plt.scatter(Xs[rargs], Ys[rargs], c="red", marker=".")
            if annot:
                list(map(annotate, zip(Xs[rargs], Ys[rargs])))
        self.Xs = Xs

    def _add_linear_trendline(self):
        line = np.poly1d(np.polyfit(self.Xs, self.points, 1))
        pred = line(self.Xs)
        r = stats.pearsonr(self.points, pred)[0] ** 2
        print("r^2 =", r)
        plt.plot(self.Xs, pred, "r--", linewidth=2)

    def _set_titles(self):
        pst = "Kontroll diagram {} paraméterhez".format(self.param["paramname"].get())
        pt = "Anyagminta: {}".format(self.param["refmaterial"].get())
        plt.title("\n".join((pst, pt)), fontsize=12)

    def _create_plot(self, trend=False, annot=True):
        gcf = plt.gcf()
        gcf.clear()
        gcf.set_size_inches(9, 5, forward=True)
        self._plot_hlines()
        ax = self._setup_axes()
        self._scatter_points(annot=annot)
        if trend:
            self._add_linear_trendline()
        self._add_zscore_axis(ax)
        self.ax.set_xlim([1, 30])
        self.ax.xaxis.set_ticks(np.arange(0, 30, 2))
        plt.tight_layout()
        plt.subplots_adjust(left=0.07, right=0.95)

    def plot(self, show=True, dumppath=None):
        self._create_plot()
        if show:
            plt.show()
        if dumppath is not None:
            plt.savefig(dumppath)
        return dumppath