from weakref import WeakKeyDictionary

from ..compat.iterable import tuple
from .proxy import DescriptorProxy

class DescriptorSet(object):
    def __init__(self, ptype, attrs=None):
        self.ptype = ptype
        self.attrs = tuple.like(attrs)
        self.registry = WeakKeyDictionary()
    def __get__(self, inst, cls):
        return (
            self.registry.get(inst) or self.registry.setdefault(
                inst, DescriptorProxy(inst, self.ptype, self.attrs))
        ) if inst else self
    def __set__(self, key, val):
        raise TypeError('DescriptorSet is read-only')
    def __delete__(self, inst):
        raise TypeError('DescriptorSet is read-only')
