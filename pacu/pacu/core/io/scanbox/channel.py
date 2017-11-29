import functools
from cStringIO import StringIO

from PIL import Image
import numpy as np
import psutil

import ujson as json
from pacu.util.inspect import repr
from pacu.util.path import Path
from pacu.util.prop.memoized import memoized_property
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, jet, gray, viridis, plasma, inferno, magma, bone, pink, spring, summer, autumn, winter, cool, Wistia, hot, PRGn, PuOr, RdGy, Spectral, coolwarm
autumn, winter, cool, Wistia, hot, PRGn, PuOr, RdGy, Spectral, coolwarm
from pacu.core.io.util.colormap.distorted2 import DistortedColormap2

colormaps = {
    'Gray': gray,
    'Jet': jet,
    'Viridis': viridis,
    'Plasma': plasma,
    'Inferno': inferno,
    'Magma': magma,
    'Bone': bone,
    'Pink': pink,
    'Spring': spring,
    'Summer': summer,
    'Autumn': autumn,
    'Winter': winter,
    'Cool': cool,
    'Wistia': Wistia,
    'Hot': hot,
    'Purple-Green': PRGn,
    'Purple-Orange': PuOr,
    'Red-Gray': RdGy,
    'Spectral': Spectral,
    'Cool-Warm': coolwarm
    }

class ScanboxChannelMeta(object):
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

class ScanboxChannel(object):
    n_focal_pane = 1 # 1 single pane
    c_focal_pane = 0 # 0 first
    def __init__(self, path, n_focal_pane=1, c_focal_pane=0):
        self.n_focal_pane = n_focal_pane
        self.c_focal_pane = c_focal_pane
        self.path = Path(path).ensure_suffix('.chan')
        self.channel = int(self.path.stem)
        self.maxppath = self.path.join_suffixes('.maxp.npy')
        self.meanppath = self.path.join_suffixes('.meanp.npy')
        self.sumppath = self.path.join_suffixes('.sump.npy')
        self.mmappath = self.path.join_suffixes('.mmap.npy')
        self.statpath = self.path.join_suffixes('.stat.npy')
        self.metapath = self.path.join_suffixes('.meta.json')
        self.cmap = colormaps['Gray']
        self.min_val = 0
        self.max_val = 255
    def import_with_io(self, io):
        print 'Import channel {}.'.format(self.channel)
        if io.mat.scanmode == 0:
            print 'Bi-directional recording.'
        else:
            print 'Uni-directional recording.'
        return self._import_with_io3(io)
    def _import_with_io3(self, io):
        height, width = map(int, io.mat.sz)
        shape = io.mat.get_shape(io.sbx.path.size)
        frame_size = height * width * 2
        depth = shape[0]
        max = np.zeros(depth, dtype='uint16')
        min = np.zeros(depth, dtype='uint16')
        mean = np.zeros(depth, dtype='float64')
        print 'Iterating over {} frames...with chunk size {}'.format(depth, frame_size)
        p = psutil.Process()
        try:
            prev_nice = p.nice()
            p.nice(5)
            prev_ionice = p.ionice()
            p.ionice(3)
        except Exception as e:
            print '[NICE] Warn: {}'.format(str(e))
        with open(self.mmappath.str, 'w') as npy, io.sbx.path.open('rb') as raw_file:
            chunks = iter(functools.partial(raw_file.read, frame_size), '')
            for i, chunk in enumerate(chunks):
                if i < depth:
                    if (i % 100) == 0:
                        mem_pct = p.memory_percent()
                        if mem_pct > 75:
                            raise MemoryError('Too much memory used. Processing aborted.')
                        print ('Processing frames at ({}/{}). '
                               'Mem usage {}%').format(i, depth, mem_pct)
                    f = ~np.frombuffer(chunk, dtype='uint16')
                    f[f == 65535] = 0
                    npy.write(f.tostring())
                    max[i] = f.max()
                    min[i] = f.min()
                    mean[i] = f.mean()
        # try:
        #     p.nice(prev_nice)
        #     p.ionice(prev_ionice.ioclass)
        # except Exception as e:
        #     print '[NICE] Warn: {}'.format(str(e))
        meta = ScanboxChannelMeta('uint16', depth, int(height), int(width))
        stat = np.rec.fromarrays([max, min, mean], names='MAX, MIN, MEAN')
        meta.save(self.metapath.str)
        np.save(self.statpath.str, stat)
        print 'Converting done!'
        return self
    @property
    def has_maxp(self):
        return self.maxppath.is_file()
    @property
    def has_meanp(self):
        return self.meanppath.is_file()
    @property
    def has_sump(self):
        return self.sumppath.is_file()
    def request_frame(self, index):
        return self.cmap8bit.to_rgba(self.mmap8bit[index], bytes=True).tostring()
    def request_projection(self, image_type):
        if image_type == 'max':
            proj = self.maxp.view('uint8')[..., 1::2]
        elif image_type == 'mean':
            proj = self.meanp.view('uint8')[..., 1::2]
        elif image_type == 'sum':
            proj = self.sump.view('uint8')[..., 1::2]
        return self.cmap8bit.to_rgba(proj, bytes=True).tostring()
    def set_cmap(self, cmap):
        self.cmap = colormaps[cmap]
    def set_contrast(self, min_val, max_val):
            self.min_val = int(min_val)
            self.max_val = int(max_val)
    @memoized_property
    def mmap8bit(self):
        return self._mmap.view('uint8'
            )[self.c_focal_pane::self.n_focal_pane, :, 1::2]
    @property
    def cmap8bit(self):
        return ScalarMappable(norm=self.norm, cmap=self.cmap)
    @property
    def norm(self):
        return Normalize(
            vmin=self.min_val, vmax=self.max_val)
    @memoized_property
    def dcmap(self):
        return DistortedColormap2('jet', xmid1=0.35, ymid1=0.65)
    #@cmap8bit.invalidator
    #def update_colormap(self, name, xmid1, ymid1, xmid2, ymid2):
    #    x1 = float(xmid1) / 100
    #    y1 = float(ymid1) / 100
    #    x2 = float(xmid2) / 100
    #    y2 = float(ymid2) / 100
    #    self.dcmap = DistortedColormap2(name,
    #        xmid1=x1, ymid1=y1, xmid2=x2, ymid2=y2)
    #def request_maxp(self, cmap_kwargs):
    #    dcmap = DistortedColormap2('gray', **cmap_kwargs)
    #    return dcmap.distorted(
    #    # return gray(
    #        self.maxp.view('uint8')[..., 1::2], bytes=True).tostring()
    def request_maxp_tiff(self):
        arr = self.maxp.view('uint8')[..., 1::2]
        i = Image.fromarray(arr)
        io = StringIO()
        i.save(io, format='tiff')
        value = io.getvalue()
        io.close()
        return value
    def request_meanp_tiff(self):
        arr = self.meanp.view('uint8')[..., 1::2]
        i = Image.fromarray(arr)
        io = StringIO()
        i.save(io, format='tiff')
        value = io.getvalue()
        io.close()
        return value
    def request_sump_tiff(self):
        arr = self.sump.view('uint8')[..., 1::2]
        i = Image.fromarray(arr)
        io = StringIO()
        i.save(io, format='tiff')
        value = io.getvalue()
        io.close()
        return value
    @memoized_property
    def maxp(self):
        return np.load(self.maxppath.str) if self.maxppath.is_file() else None
    @memoized_property
    def meanp(self):
        return np.load(self.meanppath.str) if self.meanppath.is_file() else None
    @memoized_property
    def sump(self):
        return np.load(self.sumppath.str) if self.sumppath.is_file() else None
    #@maxp.invalidator
    #def create_maxp(self):
    #    print 'Create max projection image...could take up from a few minutes to hours.'
    #    chan = self.mmap
    #    depth = len(chan)
    #    image = np.zeros_like(chan[0])
    #    p = psutil.Process()
    #    for i, frame in enumerate(chan):
    #        if (i % 500) == 0:
    #            mem_pct = p.memory_percent()
    #            if mem_pct > 75:
    #                raise MemoryError('Too much memory used. Processing aborted.')
    #            print ('Processing frames at ({}/{}). '
    #                   'Mem usage {}%').format(i, depth, mem_pct)
    #        image = np.maximum(image, frame)
    #    np.save(self.maxppath.str, image)
    #    print 'done!'
    def generate_projections(self):
        print 'Generating max, mean, and sum projection images...'
        chan = self.mmap
        depth = len(chan)
        max_image = np.zeros_like(chan[0])
        sum_image = np.zeros(chan[0].shape, dtype='float64')
        mean_image = chan[0].astype('float64')
        p = psutil.Process()
        for i, frame in enumerate(chan):
            if (i % 500) == 0:
                mem_pct = p.memory_percent()
                if mem_pct > 75:
                    raise MemoryError('Too much memory used. Aborting process.')
                print ('Processing frames at ({}/{}). '
                       'Mem usage: {}%').format(i, depth, mem_pct)
            max_image = np.maximum(max_image, frame)
            sum_image = sum_image + frame
            idx = i+1
            if idx > 1:
                img_weight = 1.0/idx
                total_weight = (idx - 1.0)/idx
                mean_image = mean_image*total_weight + frame*img_weight
        sum_image = ((2**16-1) * (sum_image/np.max(sum_image))).astype('uint16')
        mean_image = mean_image.astype('uint16')
        np.save(self.maxppath.str, max_image)
        np.save(self.meanppath.str, mean_image)
        np.save(self.sumppath.str, sum_image)
        print 'Done!'
    @memoized_property
    def stat(self):
        stat = np.load(self.statpath.str)
        return np.rec.fromrecords(stat, dtype=stat.dtype)
    @memoized_property
    def meta(self):
        return ScanboxChannelMeta.load(self.metapath.str)
    @memoized_property
    def _mmap(self):
        shape = (self.meta.z, self.meta.y, self.meta.x)
        return np.memmap(self.mmappath.str,
            mode='r', dtype=self.meta.dtype, shape=shape
        )
    @memoized_property
    def mmap(self):
        return self._mmap[self.c_focal_pane::self.n_focal_pane, ...]
    @property
    def dimension(self):
        z, y, x = self.mmap.shape
        return dict(depth=z, height=y, width=x)
    @property
    def shape(self):
        return (self.meta.z/self.n_focal_pane, self.meta.y, self.meta.x)

#import functools
#from cStringIO import StringIO
#
#from PIL import Image
#import numpy as np
#    z, y, x = self.mmap.shape
#    return dict(depth=z, height=y, width=x)
#    @property
#    def shape(self):
#        return (self.meta.z/self.n_focal_pane, self.meta.y, self.meta.x)
