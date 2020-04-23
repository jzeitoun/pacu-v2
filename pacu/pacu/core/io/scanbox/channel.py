import functools
import os
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

from pacu.core.addons import globe # Used to hold global variables for multiprocessing
from pacu.core.addons import multiprocessing # Using monkey-patched library for compatiblity with tornado websockets

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

def converter(index_set):
    blank_frames = []
    for idx in index_set:
        source_frame = globe.source[idx]
        if source_frame.max() == 0:
            blank_frames.append(idx)
        else:
            globe.sink[idx] = ~source_frame
            globe.sink[idx][globe.sink[idx]==65535] = 0 # To ensure alignment margins are black
    return blank_frames

def alt_converter(index_set):
    blank_frames = []
    for idx in index_set:
        globe.sink[idx] = globe.source[idx]
        if globe.sink[idx].max() == 0:
            blank_frames.append(idx)
    return blank_frames

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
        self.red_path = self.path.parent.joinpath('1.chan')
        self.channel = int(self.path.stem)
        self.maxppath = self.path.join_suffixes('.maxp.npy')
        self.meanppath = self.path.join_suffixes('.meanp.npy')
        self.red_sumppath = self.red_path.join_suffixes('.sump.npy')
        self.red_maxppath = self.red_path.join_suffixes('.maxp.npy')
        self.red_meanppath = self.red_path.join_suffixes('.meanp.npy')
        self.sumppath = self.path.join_suffixes('.sump.npy')
        self.mmappath = self.path.join_suffixes('.mmap.npy')
        self.metapath = self.path.join_suffixes('.meta.json')
        self.cmap = colormaps['Gray']
        self.channel_display = 'Green'
        self.min_val = 0
        self.max_val = self._mmap[self.c_focal_pane::self.n_focal_pane][0] if self.path.exists() else 65535
        self.red_min_val = 0
        self.red_max_val = self.red_mmap[self.c_focal_pane::self.n_focal_pane][0] if self.red_path.exists() else 65535
    @memoized_property
    def blue_channel(self):
        return np.zeros(self.shape[1:], dtype='uint8')
    @memoized_property
    def alpha_channel(self):
        return np.full(self.shape[1:], 255, dtype='uint8')
    def scale(self, array, min_val, max_val):
        # https://stackoverflow.com/questions/5294955/how-to-scale-down-a-range-of-numbers-with-a-known-min-and-max-value
        return  ((max_val - min_val) * (np.float64(array) - self.min_val) / (self.max_val - self.min_val)) + min_val
    def red_scale(self, array, min_val, max_val):
        # https://stackoverflow.com/questions/5294955/how-to-scale-down-a-range-of-numbers-with-a-known-min-and-max-value
        return  ((max_val - min_val) * (np.float64(array) - self.red_min_val) / (self.red_max_val - self.red_min_val)) + min_val
    def clamp(self, array):
        _array = array.copy()
        _array[_array < self.min_val] = self.min_val
        _array[_array > self.max_val] = self.max_val
        return _array
    def red_clamp(self, array):
        _array = array.copy()
        _array[_array < self.red_min_val] = self.red_min_val
        _array[_array > self.red_max_val] = self.red_max_val
        return _array
    def import_with_io(self, io):
        print 'Import channel {}.'.format(self.channel)
        if io.mat.scanmode == 0:
            print 'Bi-directional recording.'
        else:
            print 'Uni-directional recording.'
        return self._import_with_io3(io)
    def _import_with_io3(self, io):
        shape = io.mat.get_shape(io.sbx.path.size)
        depth, height, width = map(int, shape)
        print'shape: {}, {}. {}'.format(depth, height, width)
        flat_data = np.memmap(io.sbx_path.str, dtype='uint16', mode='r')
        globe.source = flat_data[self.channel::io.mat.nchannels].reshape(shape)
        globe.sink = np.memmap(self.mmappath.str, dtype='uint16', mode='w+', shape=shape)

        p = psutil.Process()
        try:
            prev_nice = p.nice()
            p.nice(5)
            prev_ionice = p.ionice()
            p.ionice(3)
        except Exception as e:
            print '[NICE] Warn: {}'.format(str(e))

        all_indices = np.arange(depth)
        if depth > 100:
            task_size = 100
            num_tasks = all_indices.shape[0] / task_size
        else:
            num_tasks = 2
        index_sets = np.array_split(all_indices, num_tasks)

        process_pool = multiprocessing.Pool(1)
        print 'Data contains {} channels and {} frames per channel'.format(io.mat.nchannels, depth)
        func = converter if not 'converted_tif' in self.path.str else alt_converter
        for i, blank_frames in enumerate(process_pool.imap_unordered(func, index_sets), 1):
            mem_pct = p.memory_percent()
            if mem_pct > 75:
                raise MemoryError('Too much memory used. Process aborted.')
            print ('Finished frame {}/{}). '
                   'Mem usage {}%').format(i*100, depth, mem_pct)
            io.blank_frames = io.blank_frames + blank_frames
        meta = ScanboxChannelMeta('uint16', depth, int(height), int(width))
        meta.save(self.metapath.str)
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
        if self.channel_display == 'Green':
            return self.cmap8bit.to_rgba(self.mmap8bit(index), bytes=True, norm=False).tostring()
            #return self.cmap8bit.to_rgba(self.mmap8bit(index), bytes=True).tostring()
        elif self.channel_display == 'Red':
            return self.cmap8bit.to_rgba(self.red_mmap8bit(index), bytes=True, norm=False).tostring()
            #return self.cmap8bit.to_rgba(self.red_mmap8bit[index], bytes=True).tostring()
        elif self.channel_display == 'Both':
            red_channel = self.red_mmap8bit(index)
            #red_channel = self.red_scale(self.red_mmap8bit[index]).astype('uint8')
            green_channel = self.mmap8bit(index)
            #green_channel = self.scale(self.mmap8bit[index]).astype('uint8')
            return np.stack((
                red_channel,
                green_channel,
                self.blue_channel,
                self.alpha_channel
                ), axis=0).transpose(1,2,0).tostring()
    def request_projection(self, image_type):
        if image_type == 'max':
            if self.maxp().dtype == 'uint8':
                proj = self.maxp()
            else:
                #proj = self.maxp.view('uint8')[..., 1::2]
                proj = self.maxp().astype('uint8')
        elif image_type == 'mean':
            if self.meanp().dtype == 'uint8':
                proj = self.meanp()
            else:
                #proj = self.meanp()).view('uint8')[..., 1::2]
                proj = self.meanp().astype('uint8')
        elif image_type == 'sum':
            if self.sump().dtype == 'uint8':
                proj = self.sump()
            else:
                #proj = self.sump.view('uint8')[..., 1::2]
                proj = self.sump().astype('uint8')
        return self.cmap8bit.to_rgba(proj, bytes=True, norm=False).tostring()
    def set_cmap(self, cmap):
        self.cmap = colormaps[cmap]
    def set_contrast(self, min_val, max_val):
        try:
            self.min_val = int(min_val)
            self.max_val = int(max_val)
        except ValueError:
            print('Invalid contrast value.')
    def set_rgb_contrast(self, min_val, max_val, red_min_val, red_max_val):
        try:
            self.min_val = int(min_val)
            self.max_val = int(max_val)
            self.red_min_val = int(red_min_val)
            self.red_max_val = int(red_max_val)
        except ValueError:
            print('Invalid contrast value.')
    def set_channel(self, channel):
        self.channel_display = channel
    #@memoized_property
    def mmap8bit(self, index):
        clamped = self.clamp(self._mmap[self.c_focal_pane::self.n_focal_pane][index])
        #return (scaled/scaled.max() * 255).astype('uint8')
        frame = self.scale(clamped, 0, 255).astype('uint8')
        return frame
        #return self._mmap.view('uint8'
        #    )[self.c_focal_pane::self.n_focal_pane, :, 1::2]
    #@memoized_property
    def red_mmap8bit(self, index):
        clamped = self.red_clamp(self.red_mmap[self.c_focal_pane::self.n_focal_pane][index])
        #return (scaled/scaled.max() * 255).astype('uint8')
        return self.red_scale(clamped, 0, 255).astype('uint8')
        #return self.red_mmap.view('uint8'
        #    )[self.c_focal_pane::self.n_focal_pane, :, 1::2]
    @property
    def cmap8bit(self):
        return ScalarMappable(cmap=self.cmap)
    @property
    def norm(self):
        if self.channel_display == 'Green':
            return Normalize(
                vmin=self.min_val, vmax=self.max_val)
        elif self.channel_display == 'Red':
            return Normalize(
                vmin=self.red_min_val, vmax=self.red_max_val)
    @memoized_property
    def dcmap(self):
        return DistortedColormap2('jet', xmid1=0.35, ymid1=0.65)
    def request_maxp_tiff(self):
        #arr = self.maxp.view('uint8')[..., 1::2]
        arr = self.maxp(export=True)
        i = Image.fromarray(arr)
        io = StringIO()
        i.save(io, format='tiff')
        value = io.getvalue()
        io.close()
        return value
    def request_meanp_tiff(self):
        #arr = self.meanp.view('uint8')[..., 1::2]
        arr = self.meanp(export=True)
        i = Image.fromarray(arr)
        io = StringIO()
        i.save(io, format='tiff')
        value = io.getvalue()
        io.close()
        return value
    def request_sump_tiff(self):
        #arr = self.sump.view('uint8')[..., 1::2]
        arr = self.sump(export=True)
        i = Image.fromarray(arr)
        io = StringIO()
        i.save(io, format='tiff')
        value = io.getvalue()
        io.close()
        return value
    def maxp(self, export=False):
        if self.channel_display == 'Green':
            proj = np.load(self.maxppath.str) if self.maxppath.is_file() else None
            if export:
                return proj
            clamped = self.clamp(proj)
            return self.scale(clamped, 0, 255).astype('uint8')
        elif self.channel_display == 'Red':
            proj = np.load(self.red_maxppath.str) if self.maxppath.is_file() else None
            clamped = self.red_clamp(proj)
            if export:
                return proj
            return self.red_scale(clamped, 0, 255).astype('uint8')
        elif self.channel_display == 'Both':
            red_proj = np.load(self.red_maxppath.str)
            green_proj = np.load(self.maxppath.str)
            if export:
                red_channel = red_pro.view('uint8')[..., 1::2].astype('uint8')
                green_channel = green_pro.view('uint8')[..., 1::2].astype('uint8')
            else:
                red_channel = self.red_scale(self.red_clamp(red_proj), 0, 255).astype('uint8')
                green_channel = self.scale(self.clamp(green_proj), 0, 255).astype('uint8')
            #red_channel = self.red_scale(np.load(self.red_maxppath.str).view('uint8')[..., 1::2]).astype('uint8')
            #green_channel = self.scale(np.load(self.maxppath.str).view('uint8')[..., 1::2]).astype('uint8')
            return np.stack((
                red_channel,
                green_channel,
                self.blue_channel,
                self.alpha_channel
                ), axis=0).transpose(1,2,0)#.tostring()
        #return np.load(self.maxppath.str) if self.maxppath.is_file() else None
    def meanp(self, export=False):
        if self.channel_display == 'Green':
            proj = np.load(self.meanppath.str) if self.meanppath.is_file() else None
            if export:
                return proj
            clamped = self.clamp(proj)
            return self.scale(clamped, 0, 255).astype('uint8')
        elif self.channel_display == 'Red':
            proj = np.load(self.red_meanppath.str) if self.meanppath.is_file() else None
            if export:
                return proj
            clamped = self.red_clamp(proj)
            return self.red_scale(clamped, 0, 255).astype('uint8')
        elif self.channel_display == 'Both':
            red_proj = np.load(self.red_meanppath.str)
            green_proj = np.load(self.meanppath.str)
            if export:
                red_channel = red_pro.view('uint8')[..., 1::2].astype('uint8')
                green_channel = green_pro.view('uint8')[..., 1::2].astype('uint8')
            else:
                red_channel = self.red_scale(self.red_clamp(red_proj), 0, 255).astype('uint8')
                green_channel = self.scale(self.clamp(green_proj), 0, 255).astype('uint8')
            #red_channel = self.red_scale(np.load(self.red_meanppath.str).view('uint8')[..., 1::2]).astype('uint8')
            #green_channel = self.scale(np.load(self.meanppath.str).view('uint8')[..., 1::2]).astype('uint8')
            return np.stack((
                red_channel,
                green_channel,
                self.blue_channel,
                self.alpha_channel
                ), axis=0).transpose(1,2,0)#.tostring()
        #return np.load(self.meanppath.str) if self.meanppath.is_file() else None
    def sump(self, export=False):
        if self.channel_display == 'Green':
            proj = np.load(self.sumppath.str) if self.sumppath.is_file() else None
            if export:
                return proj
            clamped = self.clamp(proj)
            return self.scale(clamped, 0, 255).astype('uint8')
        elif self.channel_display == 'Red':
            proj = np.load(self.red_sumppath.str) if self.sumppath.is_file() else None
            if export:
                return proj
            clamped = self.red_clamp(proj)
            return self.red_scale(clamped, 0, 255).astype('uint8')
        elif self.channel_display == 'Both':
            red_proj = np.load(self.red_sumppath.str)
            green_proj = np.load(self.sumppath.str)
            if export:
                red_channel = red_pro.view('uint8')[..., 1::2].astype('uint8')
                green_channel = green_pro.view('uint8')[..., 1::2].astype('uint8')
            else:
                red_channel = self.red_scale(self.red_clamp(red_proj), 0, 255).astype('uint8')
                green_channel = self.scale(self.clamp(green_proj), 0, 255).astype('uint8')
            #red_channel = self.red_scale(np.load(self.red_sumppath.str).view('uint8')[..., 1::2]).astype('uint8')
            #green_channel = self.scale(np.load(self.sumppath.str).view('uint8')[..., 1::2]).astype('uint8')
            return np.stack((
                red_channel,
                green_channel,
                self.blue_channel,
                self.alpha_channel
                ), axis=0).transpose(1,2,0)#.tostring()
        #return np.load(self.sumppath.str) if self.sumppath.is_file() else None
    def generate_projections(self, start, end):
        start = int(start)
        end = int(end)
        ch1_exists = self.red_path.join_suffixes('.mmap.npy').exists()
        if ch1_exists:
            channels = [self.mmap, self.red_mmap]
        else:
            channels = [self.mmap]
        for c, chan in enumerate(channels):
            chan = chan[start:end+1]
            depth = end - start
            #depth = len(chan)
            max_image = np.zeros_like(chan[start])
            sum_image = np.zeros(chan[start].shape, dtype='float64')
            mean_image = chan[start].astype('float64')
            p = psutil.Process()
            for i, frame in enumerate(chan):
                if (i % 200) == 0:
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
            sum_image = ((2**16-1) * (sum_image/(1.2*np.max(sum_image)))).astype('uint16')
            mean_image = mean_image.astype('uint16')
            if c == 0:
                np.save(self.maxppath.str, max_image)
                np.save(self.meanppath.str, mean_image)
                np.save(self.sumppath.str, sum_image)
            else:
                np.save(self.red_maxppath.str, max_image)
                np.save(self.red_meanppath.str, mean_image)
                np.save(self.red_sumppath.str, sum_image)
            print 'Done!'
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
    def red_mmap(self):
        shape = (self.meta.z, self.meta.y, self.meta.x)
        root = os.path.split(self.mmappath.str)[0]
        red_path = os.path.join(root, '1.chan.mmap.npy')
        if os.path.exists(red_path):
            return np.memmap(red_path,
                mode='r', dtype=self.meta.dtype, shape=shape
            )
        else:
            red_path = os.path.join(root, '0.chan.mmap.npy')
            return np.memmap(red_path,
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
