import numpy as np

import unittest

from CQC.backend.cchart import ControlChart


class TestControlChart(unittest.TestCase):

    def setUp(self):
        self.header = ["TestMethod", "TestEtalon",
                       1, "TestParam", "T/t",
                       "2000-01-01 00:00:00"]
        self.points = np.linspace(1, 5, 30)
        self.dates = np.arange(1, 30)

    def test_initialization(self):
        cc = ControlChart(*self.header)
