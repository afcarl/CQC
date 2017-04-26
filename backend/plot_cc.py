import numpy as np
from scipy import stats

from matplotlib import pyplot as plt

cacheroot = "/home/csa/SciProjects/Project_CQC/"


class PlotBuilder(object):

    def __init__(self, cc):
        self.cc = cc
        self.ax = plt.gca()

    def _plot_hlines(self):

        def draw_stdline(parm):
            coef, col = parm
            plt.axhline(y=self.cc.refmean + coef * self.cc.refstd, xmin=datemin, xmax=datemax, color=col)

        datemin = np.min(self.cc.dates)
        datemax = np.max(self.cc.dates)
        plt.axhline(y=self.cc.refmean, xmin=datemin, xmax=datemax, color="purple", linestyle="--")

        list(map(draw_stdline, ((2, "blue"), (-2, "blue"),
                                (3, "red"), (-3, "red"))))
        plt.axhline(y=self.cc.refmean+self.cc.uncertainty, xmin=datemin, xmax=datemax, color="green")
        plt.axhline(y=self.cc.refmean-self.cc.uncertainty, xmin=datemin, xmax=datemax, color="green")

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
        zax.set_yticklabels(abs(i) for i, item in enumerate(ax.get_yticklabels(), start=-4))

    def _scatter_points(self, annot):

        def annotate(arg):
            date, point = arg
            z = (point - self.cc.refmean) / self.cc.refstd
            z = round(z, 2)
            va = "top" if z < 0 else "bottom"
            z = abs(z)
            tx = "{} {}\nZ° = {}".format(round(point, 4), self.cc.dimension, z)
            # offsx = 10. if point > self.cc.refmean else -10.
            # offsy = 20. if date > np.mean(self.cc.dates) else -10.
            offsx = 0
            offsy = 0
            self.ax.annotate(tx, xy=(date, point), xycoords="data",
                             xytext=(offsx, offsy), textcoords="offset points",
                             # xytext=(0.8, 0.95), textcoords="axes fraction",
                             horizontalalignment="right", verticalalignment=va)

        Xs, Ys = np.array(self.cc.dates), np.array(self.cc.points)
        ywlim = self.cc.refmean - 1.9 * self.cc.refstd, self.cc.refmean + 1.9 * self.cc.refstd
        rdlim = self.cc.refmean - 2.9 * self.cc.refstd, self.cc.refmean + 2.9 * self.cc.refstd
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

    def _add_linear_trendline(self):
        z = np.polyfit(self.cc.dates.astype(int), self.cc.points, 1)
        p = np.poly1d(z)
        r = stats.pearsonr(self.cc.points, p(self.cc.dates.astype(int)))[0] ** 2
        print("r^2 =", r)
        plt.plot(self.cc.dates, p(self.cc.dates.astype(int)), "r--", linewidth=3)

    def _set_titles(self):
        pst = "Kontroll diagram {} paraméterhez".format(self.cc.paramname)
        pt = "Anyagminta: {}\n{}. revízió".format(self.cc.etalon_ID, self.cc.revision)
        plt.title("\n".join((pst, pt)), fontsize=12)

    def _create_plot(self, trend=False, annot=True):
        gcf = plt.gcf()
        gcf.clear()
        gcf.set_size_inches(10, 6, forward=True)
        self._plot_hlines()
        ax = self._setup_axes()
        self._scatter_points(annot=annot)
        if trend:
            self._add_linear_trendline()
        self._add_zscore_axis(ax)
        self._set_titles()
        plt.tight_layout()
        plt.subplots_adjust(left=0.07, right=0.95)

    def plot(self):
        self._create_plot()
        plt.show()

    def dump(self, path=None):
        self._create_plot()
        plt.savefig(path if path is not None else cacheroot + "cc_pic.png")
