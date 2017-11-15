from __future__ import division

from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

import ujson as json
from pacu.util.path import Path
from pacu.util.inspect import repr
from pacu.util.prop.memoized import memoized_property

class TrajectoryChannelMeta(object):
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

class TrajectoryChannel(object):
    indices = slice(None)
    cmap_name = 'jet'
    def __init__(self, path):
        self.path = Path(path)
    def set_indices(self, indices):
        self.indices = indices
        return self
    @property
    def alogpath(self):
        return self.path.with_suffix('.alog.npy')
    @property
    def mmappath(self):
        return self.path.with_suffix('.mmap.npy')
    @property
    def timepath(self):
        return self.path.with_suffix('.time.npy')
    @property
    def statpath(self):
        return self.path.with_suffix('.stat.npy')
    @property
    def metapath(self):
        return self.path.with_suffix('.meta.json')
    @memoized_property
    def cmap8bit(self):
        norm = Normalize(
            vmin=self.stat.MIN.min()/256, vmax=self.stat.MAX.max()/256)
        return ScalarMappable(norm=norm, cmap=plt.get_cmap(self.cmap_name))
    @cmap8bit.invalidator
    def set_cmap(self, which=0):
        name = ['jet', 'gray', 'hot', 'hsv'][int(which)]
        self.cmap_name = name
    @memoized_property
    def mmap(self): # indices
        meta = TrajectoryChannelMeta.load(self.metapath.str)
        shape = (meta.z, meta.y, meta.x)
        return np.memmap(self.mmappath.str,
            mode='r', dtype=self.meta.dtype, shape=shape
        )[self.indices]
    @memoized_property
    def mmap8bit(self):
        return self.mmap.view('uint8')[..., 1::2]
    @memoized_property
    def meta(self): # indices
        meta = TrajectoryChannelMeta.load(self.metapath.str)
        if not isinstance(self.indices, slice):
            meta.z = self.indices.sum()
        return meta
    @memoized_property
    def stat(self): # indices
        stat = np.load(self.statpath.str)
        return np.rec.fromrecords(stat, dtype=stat.dtype
        )[self.indices]
    @memoized_property
    def time(self): # indices
        return np.load(self.timepath.str)[self.indices]
    @property
    def duration(self):
        return self.time[-1] - self.time[0]
    @property
    def framerate(self):
        return len(self.mmap) / self.duration
    @memoized_property
    def alog(self): # indices
        alog = np.load(self.alogpath.str)
        return np.rec.fromrecords(alog, dtype=alog.dtype
        )[self.indices]
    @memoized_property
    def original_velocity(self):
        alog = np.load(self.alogpath.str)
        return np.rec.fromrecords(alog, dtype=alog.dtype).V
    def import_raw(self, tiff, timestamps, log):
        print 'Align log and timestamp...'
        log_aligned = log.align(timestamps)
        print 'Extracting metadata...'
        meta = TrajectoryChannelMeta(tiff.dtype.name, *tiff.shape)
        print 'Calculating basic statistics...'
        max = tiff.max(axis=(1,2))
        min = tiff.min(axis=(1,2))
        mean = tiff.mean(axis=(1,2))
        stat = np.rec.fromarrays([max, min, mean], names='MAX, MIN, MEAN')
        mmap = np.memmap(self.mmappath.str,
            mode='w+', dtype=tiff.dtype, shape=tiff.shape)
        print 'Write to disk...'
        mmap[:] = tiff[:]
        meta.save(self.metapath.str)
        np.save(self.statpath.str, stat)
        np.save(self.timepath.str, timestamps)
        np.save(self.alogpath.str, log_aligned)
        print 'Converting done!'
        return self
    def toDict(self):
        z, y, x = self.mmap.shape
        return dict(depth=z, height=y, width=x)
    def request_frame(self, index):
        return self.cmap8bit.to_rgba(self.mmap8bit[index], bytes=True).tostring()





