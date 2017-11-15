import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

class DistortedColormap(object):
    """
    dcm = DistortedColormap('jet', xmid=0.75, ymid=0.5)
    dcm.distorted
    """
    n = 100 # number of space element
    def __init__(self, name='jet', vmin=0.0, vmax=1.0, xmid=0.5, ymid=0.5):
        self.name = name
        self.original = cm.get_cmap(name)
        self.set_lim(vmin, vmax)
        self.set_mid(xmid, ymid)
    def set_lim(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
    def set_mid(self, xmid, ymid):
        self.xmid = xmid
        self.ymid = ymid
    @property
    def space(self):
        space1 = np.linspace(self.vmin, self.ymid, self.n*self.xmid, endpoint=False)
        space2 = np.linspace(self.ymid, self.vmax, self.n - self.n*self.xmid)
        return np.concatenate((space1, space2))
    @property
    def distorted(self):
        return LinearSegmentedColormap.from_list(
            repr(self), self.original(self.space))
    def __repr__(self):
        return ('{}(name={s.name!r}, vmin={s.vmin}, vmax={s.vmax}, '
            'xmid={s.xmid}, ymid={s.ymid})').format(type(self).__name__, s=self)

# from matplotlib import pyplot as plt
# dcmap = DistortedColormap('jet', xmid=0.75, ymid=0.75)
# arr = np.linspace(0, 100, 100).reshape((10, 10))
# fig, ax = plt.subplots(ncols=2)
# ax[0].imshow(arr, interpolation='nearest', cmap=dcmap.original)
# ax[1].imshow(arr, interpolation='nearest', cmap=dcmap.distorted)
# plt.show()
