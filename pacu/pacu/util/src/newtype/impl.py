"""
Another easy way to define and use metaclass.
"""

from warnings import warn
from weakref import WeakKeyDictionary

from .incremental_hash import IncrementalHash
from ..descriptor.set import DescriptorSet

shadow = (
    u'An attribute `{!r}` defined in the class `{}` as `{}` '
    u'will be shadowed by a property defined in `{}` metaclass.')

class type_attr(IncrementalHash):
    def __init__(self, func):
        self.func = func
        self.registry = WeakKeyDictionary()
    def __set__(self, inst, value):
        raise Exception('Meta attribute is a read-only descriptor.')
    def __get__(self, inst, type):
        return self.registry[inst] if inst else None
    def update(self, inst, type, *args):
        value = self.func(inst, *args)
        self.registry[inst] = value

origin = type
class newtype(origin):
    meta = DescriptorSet(type_attr)
    def __new__(mcl, name, bases, nmspc):
        cls = super(newtype, mcl).__new__(mcl, name, bases, nmspc)
        cls.meta.map.update(name, bases, nmspc)
        for key in cls.meta.key:
            if key in nmspc:
                warn(shadow.format(nmspc[key], key, name, mcl.__name__))
        return cls
    @classmethod
    def base(type, *bases, **nmspc):
        name = '{}TypeBase'.format(type.__name__)
        return type(name, bases, nmspc)
    attr = type_attr

def test():
    class mutant(newtype):
        pass
    assert mutant.base(float)(1.6) == float(1.6)
    assert mutant.base(str, a=1)().a == 1
    assert mutant.base(int)(20) == 20
    assert mutant.base(str)('a1num').isalnum()
