from __future__ import division


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from ipdb import set_trace

import ujson as json
from pacu.util.path import Path
from pacu.util.inspect import repr
from pacu.util.prop.memoized import memoized_property
from pacu.core.io.scanimage.legacy.cfaan import driftcorrect

from pacu.core.io.util.colormap.distorted import DistortedColormap

class ScanimageChannelMeta(object):
    __repr__ = repr.auto_strict
    def __init__(self, dtype, z, y, x):
        self.dtype = dtype
        self.z = z
        self.y = y
        self.x = x
    def save(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self.__dict__))
    @classmethod
    def load(cls, path):
        with open(path) as f:
            payload = json.loads(f.read())
        return cls(**payload)

class ScanimageChannel(object):
    cmap_name = 'jet'
    def __init__(self, path):
        self.path = Path(path)
        self.dcmap = DistortedColormap('jet', xmid=0.5, ymid=0.5)
    @property
    def mmappath(self):
        return self.path.with_suffix('.mmap.npy')
    @memoized_property
    def norm(self):
        return Normalize(
            vmin=self.stat.MIN.min()/256, vmax=self.stat.MAX.max()/256)
    @memoized_property
    def cmap8bit(self):
        return ScalarMappable(norm=self.norm, cmap=self.dcmap.distorted)
    @cmap8bit.invalidator
    def update_colormap(self, name, xmid, ymid):
        x = float(xmid) / 100
        y = float(ymid) / 100
        self.dcmap = DistortedColormap(name, xmid=x, ymid=y)
    @memoized_property
    def mmap(self):
        shape = (self.meta.z, self.meta.y, self.meta.x)
        return np.memmap(self.mmappath.str,
            mode='r', dtype=self.meta.dtype, shape=shape)
    @memoized_property
    def mmap8bit(self):
        return self.mmap.view('uint8')[..., 1::2]
    @property
    def metapath(self):
        return self.path.with_suffix('.meta.json')
    @memoized_property
    def meta(self):
        return ScanimageChannelMeta.load(self.metapath.str)
    @property
    def statpath(self):
        return self.path.with_suffix('.stat.npy')
    @memoized_property
    def stat(self):
        stat = np.load(self.statpath.str)
        return np.rec.fromrecords(stat, dtype=stat.dtype)
    def import_raw(self, tiff):
        print 'Drift correct...each step may take a few minutes...'
        drift = driftcorrect.getdrift3(tiff)
        print 'Got drift data...try to correct.'
        corr = driftcorrect.driftcorrect2(tiff, drift)
        print 'Extracting metadata...'
        meta = ScanimageChannelMeta(corr.dtype.name, *corr.shape)
        print 'Calculating basic statistics...'
        max = corr.max(axis=(1,2))
        min = corr.min(axis=(1,2))
        mean = corr.mean(axis=(1,2))
        stat = np.rec.fromarrays([max, min, mean], names='MAX, MIN, MEAN')
        mmap = np.memmap(self.mmappath.str,
            mode='w+', dtype=corr.dtype, shape=corr.shape)
        print 'Write to disk...'
        mmap[:] = corr[:]
        meta.save(self.metapath.str)
        np.save(self.statpath.str, stat)
        print 'Converting done!'
        return self
    def toDict(self):
        z, y, x = self.mmap.shape
        return dict(depth=z, height=y, width=x)
    def request_frame(self, index):
        # frame = self.mmap8bit[index]
        # self.cmap8bit.set_clim(frame.min(), frame.max())
        # return self.cmap8bit.to_rgba(frame, bytes=True).tostring()
        return self.cmap8bit.to_rgba(self.mmap8bit[index], bytes=True).tostring()
