class MeasurementSeries:

    def __init__(self, dates, values):
        self.dates = dates
        self.values = values

    @property
    def mean(self):
        return self.values.mean()

    @property
    def std(self):
        return self.values.std()

    @property
    def stats(self):
        return self.mean, self.std
