import numpy as np

class TrajectoryFilter(object):
    id = 'filter'
    filterName = None
    activePassValue = None
    passivePassValue = None
    _indices = []
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def toDict(self):
        return dict(
            filterName = self.filterName,
            activePassValue = self.activePassValue,
            passivePassValue = self.passivePassValue)
        # moving_indices = qwe.channel.alog.V > qwe.channel.alog.V.mean()
    def make_indices(self, velo):
        table = {
            'active-pass': self.make_active_indices,
            'passive-pass': self.make_passive_indices,
            'positive-pass': self.make_positive_indices,
        }
        func = table.get(self.filterName, self.bypass)
        return func(velo)
    def make_positive_indices(self, velo):
        return velo > 0
    def make_active_indices(self, velo):
        if self.activePassValue:
            return velo > int(self.activePassValue)
        return velo != np.nan
    def make_passive_indices(self, velo):
        if self.passivePassValue:
            return velo < int(self.passivePassValue)
        return velo != np.nan
    def bypass(self, velo):
        return None
