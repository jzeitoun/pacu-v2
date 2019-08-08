from __future__ import division

import time
import os
from collections import namedtuple

import numpy as np
from scipy import io

from pacu.core.io.view.zero_dimension_array import ZeroDimensionArrayView
from pacu.util.path import Path
from pacu.profile import manager

opt = manager.instance('opt')

Dimension = namedtuple('Dimension', 'height, width')

class ScanboxMatView(ZeroDimensionArrayView):
    def __init__(self, path):
        self.path = Path(path).ensure_suffix('.mat')
        self.bound_sbx_path = self.path.with_suffix('.sbx')
        array = io.loadmat(self.path.str, squeeze_me=True).get('info')
        super(ScanboxMatView, self).__init__(array)
    @property
    def is_aligned(self):
        return self.path.name.startswith('Aligned')
    @property
    def sbxsize(self):
        #return self.path.with_suffix('.sbx').size
        return Path(self.stempath).with_suffix('.sbx').size
    @property
    def sbxtime(self):
        #return self.path.with_suffix('.sbx').created_at
        return Path(self.stempath).with_suffix('.sbx').created_at
    @property
    def sbxpath(self):
        #return self.path.with_suffix('.sbx').relative_to(opt.scanbox_root)
        #return Path(os.path.split(self.stempath)[1]).with_suffix('.sbx')
        return Path(self.stempath).with_suffix('.sbx').relative_to(opt.scanbox_root)
    @property
    def iopath(self):
        return self.sbxpath.with_suffix('.io')
    @property
    def shape(self):
        return tuple(reversed((self.nframes, self.channels) + self.dimension))
    @property
    def dimension(self):
        return Dimension(*self.sz)
    @property
    def nframes(self):
        nframes = int(self.sbxsize/self.recordsPerBuffer/
                self.dimension.width/2/self.channels)
        return nframes * (1 if self.scanmode else 2)
    @property
    def framerate(self):
        # recordsPerBuffer = self.originalRecordsPerBuffer \
        #                 if self.is_aligned else self.recordsPerBuffer
        if self.is_aligned:
            try:
                recordsPerBuffer = self.originalRecordsPerBuffer
            except:
                recordsPerBuffer = self.recordsPerBuffer
        else:
            recordsPerBuffer = self.recordsPerBuffer
        rate = self.resfreq / recordsPerBuffer
        return rate if self.scanmode else rate * 2
    @property
    def nchannels(self):
        if self.channels == -1:
            if self.chan.nchan == 1:
                return 1
            else:
                return 2
        elif self.channels == 1:
            return 2
        else:
            return 1
        #return 2 if self.channels == 1 else 1 (JZ) For compatibility with mesoscope
    @property
    def factor(self):
        if self.channels == -1:
            if self.chan.nchan == 1:
                return 2
            else:
                return 1
        elif self.channels == 1:
            return 1
        else:
            return 2
        #return 1 if self.channels == 1 else 2 (JZ) For compatibility with mesoscope
    @property
    def scanmodestr(self):
        return 'uni' if self.scanmode == 1 else 'bi'
    def get_max_idx(self, size):
        return int(size/self.recordsPerBuffer/self.sz[1]*self.factor/4 - 1)
    def get_shape(self, size):
        return self.get_max_idx(size) + 1, self.recordsPerBuffer, self.sz[1]
    @property
    def recordsPerBuffer(self):
        rpb = self._dict.get('recordsPerBuffer')
        return rpb * 2 if self.scanmode is 0 else rpb
#     def __dir__(self): # quick and dirty: need to use descriptor set
#         return super(ScanboxInfoView, self).__dir__() + \
#             'path nchan factor framerate recordsPerBuffer sz'.split()
    @property
    def activeChannels(self):
        channels = self.channels
        if channels == -1:
            activeChannels = self.chan.sample
            if activeChannels[0] and activeChannels[1]:
                return ['Green', 'Red', 'Both']
            elif activeChannels[0] and not activeChannels[1]:
                return ['Green']
            elif activeChannels[1] and not activeChannels[0]:
                return ['Red']
        elif channels == 0:
            return ['Green', 'Red', 'Both']
        elif channels == 1:
            return ['Green']
        elif channels == 2:
            return ['Red']

    def toDict(self):
        data = self.items()
        data['iopath'] = str(self.iopath)
        data['framerate'] = self.framerate
        data['frameratestr'] = str(self.framerate) + ' fps'
        data['sbxsize'] = self.sbxsize.str
        data['sbxtime'] = time.mktime(self.sbxtime.timetuple())
        data['sbxpath'] = self.sbxpath.str
        data['nchannels'] = self.nchannels
        data['nframes'] = self.nframes
        data['nframesstr'] = str(self.nframes) + ' frames'
        data['scanmodestr'] = self.scanmodestr
        data['focal_pane_args'] = self.focal_pane_args
        return data
    @property
    def duration(self):
        return self.nframes / self.framerate
        # return '{s.nframes} frames at {s.framerate} fps is 00:01:14:01'.format(s=self)
        #  duration = frame_count / frame_rate
#     @property
#     def originalRecordsPerBuffer(self):
#         obuf = self._dict.get('originalRecordsPerBuffer')
#         buf = self.recordsPerBuffer
#         print 'original: {}, normal: buf'.format(obuf, buf)
#         return obuf or buf
    @property
    def focal_pane_args(self):
        try:
            if self.volscan:
                _, _, n = map(int, self.otparam)
            else:
                n = 1
        except:
            n = 1
        try:
            if self.volscan:
                waves = list(map(int, self.otwave))
            else:
                waves = [0]
        except:
            waves = [0]
        return dict(waves=waves, n=n)
    @property
    def memmap(self): # first channel
        shape = self.get_shape(self.bound_sbx_path.size)
        chans = np.memmap(self.bound_sbx_path.str, dtype='uint16', mode='r', shape=shape)
        return chans[0::mat.nchannels]
    @property
    def opened(self):
        return self.bound_sbx_path.open('rb')

# import psutil
# import functools
# p = psutil.Process()
# mat = ScanboxMatView('/Volumes/Users/ht/dev/current/pacu/tmp/sbxroot/Dario/P22_000_004.mat')
# h, w = map(int, mat.sz)
# mm = mat.memmap
# frame_size = h * w * 2
# raw = mat.opened
# for index, chunk in enumerate(iter(functools.partial(raw.read, frame_size), '')):
#     print index, p.memory_percent()
#     print chunk == mm[index].tostring()
#     break
