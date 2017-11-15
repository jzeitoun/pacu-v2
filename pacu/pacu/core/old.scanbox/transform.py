
from pysbx.util.inspect import repr

class Transform(object):
    def __init__(self, entity):
        self.entity = entity
    def verify_entity(self):
        pass
    def write(self):
        pass
    __repr__ = repr.auto_strict

import numpy as np

from pysbx.core.process.transform.common import Transform

class TIFFStack(Transform):
    def transform(self, start=0, end=-1):
        fp = np.memmap(self.entity.raw.file, dtype='uint16',
                mode='r', shape=self.entity.mt_shape, order='F')
        fp = np.iinfo(np.uint16).max - fp.transpose(3, 1, 0, 2)[start:end]
        return fp[..., 0]
