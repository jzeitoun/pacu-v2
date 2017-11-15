import numpy as np
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

class DistortedColormap2(object):
    """
    dcm = DistortedColormap('jet', xmid1=0.5, ymid1=0.5, xmid2=0.5, ymid2=0.5)
    dcm.distorted
    """
    n = 100 # number of space element
    def __init__(self, name='jet', vmin=0.0, vmax=1.0,
            xmid1=0.25, ymid1=0.25, xmid2=0.75, ymid2=0.75):
        self.name = name
        self.original = cm.get_cmap(name)
        self.set_lim(vmin, vmax)
        self.set_mid(xmid1, ymid1, xmid2, ymid2)
    def set_lim(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
    def set_mid(self, xmid1, ymid1, xmid2, ymid2):
        self.xmid1 = xmid1
        self.ymid1 = ymid1
        self.xmid2 = xmid2
        self.ymid2 = ymid2
    @property
    def space(self):
        space1 = np.linspace(self.vmin, self.ymid1, self.n*self.xmid1, endpoint=False)
        space2 = np.linspace(self.ymid1, self.ymid2, self.n - self.n*(self.xmid2-self.xmid1), endpoint=False)
        space3 = np.linspace(self.ymid2, self.vmax, self.n - self.n*(self.vmax-self.xmid2))
        return np.concatenate((space1, space2, space3))
    @property
    def distorted(self):
        return LinearSegmentedColormap.from_list(
            repr(self), self.original(self.space))
    def __repr__(self):
        return ('{}(name={s.name!r}, vmin={s.vmin}, vmax={s.vmax}, '
            'xmid1={s.xmid1}, ymid1={s.ymid1})'
            'xmid2={s.xmid2}, ymid2={s.ymid2})'
        ).format(type(self).__name__, s=self)

# from matplotlib import pyplot as plt
# dcmap = DistortedColormap2('jet', xmid1=0.25, ymid1=0.25, xmid2=0.75, ymid2=0.75)
# arr = np.linspace(0, 100, 100).reshape((10, 10))
# fig, ax = plt.subplots(ncols=2)
# ax[0].imshow(arr, interpolation='nearest', cmap=dcmap.original)
# ax[1].imshow(arr, interpolation='nearest', cmap=dcmap.distorted)
# plt.show()
