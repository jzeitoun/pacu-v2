from cPickle import loads, dumps, PicklingError
from weakref import WeakKeyDictionary

import tifffile
import numpy as np

from pacu.core.svc.analysis.i3d.rois.node.base import BaseNode
from pacu.util.descriptor.set import DescriptorSet

class NotDefined(object):
    pass

class TypeDescriptor(object):
    on_set_func = None
    def __init__(self, type, default=NotDefined):
        self.type = type
        self.default = default
        self.registry = WeakKeyDictionary()
    def assign(self, inst, value):
        if not isinstance(value, self.type):
            raise TypeError(
                'Value `{}` should be `{}`'.format(value, self.type))
        self.registry[inst] = value
    def __set__(self, inst, value):
        self.assign(inst, value)
        if self.on_set_func:
            self.on_set_func(inst)
    def __get__(self, inst, type):
        return (self if not inst else
                self.registry[inst] if inst in self.registry else
                self.default)
    def on_set(self, func):
        self.on_set_func = func
        return func

class BaseROI(object):
    PICKLE_PROTOCOL = 2
    def __init__(self, mmap):
        BaseROI.mmap.assign(self, mmap)
    mmap = TypeDescriptor(np.ndarray)
    shape = TypeDescriptor(tuple)
    mean = BaseNode(np, axis=(1,2))
    sum = BaseNode(np, axis=(1,2))
    std = BaseNode(np, axis=(1,2))
    nodes = DescriptorSet(BaseNode)
    def invalidate_nodes(self):
        return self.nodes.map.invalidate()
    def __getstate__(self):
        try:
            return dict(self.nodes.items())
        except Exception as e:
            raise PicklingError('Unable to pickle: {}'.format(e))
    @property
    def as_pickle(self):
        return dumps(self, self.PICKLE_PROTOCOL)
    @property
    def as_persistent(self):
        return dict(
            type='ROI',
            modname=self.__module__,
            clsname=type(self).__name__,
            data=self.as_pickle
        )

flame = np.load('/Volumes/Users/ht/roitest/flame.short.delme.npy')
roi = BaseROI(flame[:, 50:56, 70:76])
