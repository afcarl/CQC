from tkinter import Tk

import numpy as np

from backend.cchart import ControlChart
from backend.parameter import Parameter


mean = 1.
std = 2.
unc = 5.5

data = ("2017.08.01", "TestMaterial", mean, std, unc,
        "TestParam", "GigaTest", "Teszt Elek", "No Comment")

points = np.random.normal(mean, std, size=30)

tk = Tk()

cc = ControlChart(Parameter.from_values(dict(zip(Parameter.paramnames, data))), "TesztCC", points)
cc.plot(show=True)

