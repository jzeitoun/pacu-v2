from __future__ import division

import os

import numpy as np
from scipy import io

from pacu.util.descriptor.set import DescriptorSet

class MatMapper(object):
    fields = (
        ('resfreq', 'resfreq'),
        ('postTriggerSamples', ''),
        ('recordsPerBuffer', 'records_per_buffer'),
        ('bytesPerBuffer', ''),
        ('channels', 'channels'),
        ('ballmotion', ''),
        ('abort_bit', ''),
        ('scanbox_version', 'version'),
        ('config', 'config'),
        ('messages', ''),
    )
    raw = None
    path = None
    error = None
    @classmethod
    def with_error(cls, e):
        self = cls.__new__(cls)
        self.error = e
        return self
    @classmethod
    def can_deal_with(cls, mat_route):
        mat_route = str(mat_route)
        if mat_route.endswith('.mat'):
            mat_route = mat_route[:-4]
        try:
            mat = io.loadmat(mat_route, squeeze_me=True)['info']
            hasfields = all(k in mat.dtype.names for k, f in cls.fields)
        except:
            mat, hasfields = False, False
        hassbx = os.path.isfile(mat_route + '.sbx')
        return all((mat, hasfields, hassbx))

    def __init__(self, path):
        # if '.' in path.str:
        #     path = path.with_suffix(''.join(path.suffixes + ['.mat']))
        self.path = path.with_suffix('.mat')
        self.raw = io.loadmat(self.path.str, squeeze_me=True)['info']
        self.parse()
    def __nonzero__(self):
        return not bool(self.error)
    def parse(self):
        for key, field, in self.fields:
            if field:
                setattr(self, field, self.raw[key][()])
    @property
    def size(self):
        return os.path.getsize(self.path.with_suffix('.sbx').str)
    @property
    def nchan(self):
        return 2 if self.channels is 1 else 1
    @property
    def factor(self):
        return 1 if self.channels is 1 else 2
    @property
    def framerate(self):
        return self.resfreq / self.records_per_buffer
    @property
    def max_index(self):
        return int(self.size/self.records_per_buffer/796*self.factor/4)
    @property
    def mt_shape(self):
        return (796, self.records_per_buffer, self.nchan, self.max_index)
    @property
    def memmap(self):
        sbx = self.path.with_suffix('.sbx').open('rb')
        return np.memmap(sbx, dtype='uint16',
                mode='r', shape=self.mt_shape, order='F'
            ).transpose(3, 1, 0, 2)

    props = DescriptorSet(property, 'size framerate max_index mt_shape')

# from pacu.util.path import Path
# kj = Path('/Volumes/Users/ht/tmp/pysbx-data/KJ13.2_000_000')
# qwe = MatMapper(kj)
