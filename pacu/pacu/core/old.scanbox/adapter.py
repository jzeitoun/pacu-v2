from __future__ import division

import os
from collections import OrderedDict
from collections import namedtuple

import numpy as np
from scipy import io

from pacu.util.inspect import repr
from pacu.util.format.table import simple
from pacu.util.path import Path
from pacu.util.prop.memoized import memoized_property

def show(self):
    print simple.show('METADATA', self.export())
    if self.raw:
        print self.raw
        print '{:,} Bytes'.format(self.raw.size)
    else:
        print 'No corresponding raw data found.'

def export(self):
    meta = [(key, val) for key, val in vars(self).items() if key not in ['usernotes', 'config', 'ballmotion', 'messages']]
    config = [(key, val) for key, val in vars(self.config).items() if key != 'zstack']
    zstack = [(key, val) for key, val in vars(self.config.zstack).items()]
    props = [(key, getattr(self, key)) for key in 'nchan factor framerate max_index'.split()]
    return props + meta + config + zstack

@property
def nchan(self):
    return 2 if self.channels is 1 else 1
@property
def factor(self):
    return 1 if self.channels is 1 else 2
@property
def framerate(self):
    return self.resfreq / self.recordsPerBuffer
@property
def max_index(self):
    return int(self.raw.size/self.recordsPerBuffer/796*self.factor/4)
@property
def mt_shape(self):
    return (796, self.recordsPerBuffer, self.nchan, self.max_index)

class RawData(object):
    def __init__(self, filename, meta):
        self.filename = filename
        self.size = os.path.getsize(filename)
        self.file = open(filename)
        self.meta = meta
    __repr__ = repr.auto_strict

    @classmethod
    def from_metadata_filename(cls, filename, meta):
        sbxpath = Path(filename).with_suffix('.sbx')
        if sbxpath.is_file():
            return cls(sbxpath.str, meta)
    @memoized_property
    def memmap(self):
        return np.memmap(self.meta.raw.file, dtype='uint16',
                mode='r', shape=self.meta.mt_shape, order='F').transpose(3, 1, 0, 2)


def to_ntuple(clsname, keys, vals):
    return namedtuple(clsname, keys)(*vals)

def get_meta(filename):
    info = io.loadmat(filename, squeeze_me=True)['info']
    meta = to_ntuple('MetaData', info.dtype.names, info.item())
    config = to_ntuple('Config', meta.config.dtype.names, meta.config.tolist())
    zstack = to_ntuple('Zstack', config.zstack.dtype.names,
            map(int, config.zstack.item()))
    meta = meta._replace(config=config._replace(zstack=zstack))
    type(meta).show = show
    type(meta).export = export
    type(meta).factor = factor
    type(meta).nchan = nchan
    type(meta).framerate = framerate
    type(meta).max_index = max_index
    type(meta).mt_shape = mt_shape
    type(meta).raw = RawData.from_metadata_filename(filename, meta)
    return meta

def test():
    mat = '/Volumes/Users/ht/tmp/pysbx-data/JZ6/JZ6_000_003.mat'
    raw = io.loadmat(mat, squeeze_me=True)['info']
    return get_meta(mat)
