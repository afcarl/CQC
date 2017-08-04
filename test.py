from tkinter import Tk

import numpy as np

from backend.cchart import ControlChart
from backend.parameter import CCParam


mean = 1.
std = 2.
unc = 5.5

data = ("2017.08.01", "TestMaterial", mean, std, unc,
        "TestParam", "GigaTest", "Teszt Elek", "No Comment")

points = np.random.normal(mean, std, size=30)

tk = Tk()

cc = ControlChart(CCParam.from_values(dict(zip(CCParam.paramnames, data))), "TesztCC", points)
cc.plot(show=True)

