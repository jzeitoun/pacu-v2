from functools import wraps
from weakref import WeakKeyDictionary

from pacu.util.newtype.incremental_hash import IncrementalHash

class NotComputed(object):
    pass

class BaseNode(IncrementalHash):
    def __init__(self, nmspc, *args, **kwargs):
        self.registry = WeakKeyDictionary()
        self.nmspc = nmspc
        self.args = args
        self.kwargs = kwargs
    def __key_set__(self, key):
        self.method = getattr(self.nmspc, key)
        return key
    def getter(self, inst):
        return self.method(inst.mmap, *self.args, **self.kwargs)
    def __get__(self, inst, type, key):
        return (self if not inst else
                self.registry[inst] if inst in self.registry else
                self.registry.setdefault(inst,
                    inst.__dict__.get(key)
                        if key in inst.__dict__ else
                    self.getter(inst)
                ))
    def __delete__(self, inst):
        v_desc = self.registry.pop(inst, NotComputed)
        v_inst = inst.__dict__.pop(self.__key__, NotComputed)
        return v_inst if v_desc is NotComputed else v_desc
    def invalidate(self, inst, type):
        return self.__delete__(inst)
