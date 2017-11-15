from functools import wraps
from weakref import WeakKeyDictionary

from ...newtype.incremental_hash import IncrementalHashBase
from ...newtype.impl import newtype

class weakkeySupport(newtype):
    def __call__(cls, *args, **kwargs):
        self = cls.__new__(cls, *args, **kwargs)
        self.registry = WeakKeyDictionary()
        self.__init__(*args, **kwargs)
        return self

class MemoMix(weakkeySupport.base(IncrementalHashBase)):
    def __by_func__(self, value):
        return value
    def by(self, func):
        self.__by_func__ = func
        return self
    def __get__(self, inst, cls):
        return (self if not inst else self.registry[inst]) # if inst in registry else)
                # registry.setdefault(inst, self.__mz_getter__(inst)))
    def __set__(self, inst, value):
        self.registry[inst] = self.__by_func__(value)
    def __delete__(self, inst):
        self.registry.pop(inst, None)
    def invalidator(self, func):
        @wraps(func)
        def wrapper(inst, *args, **kwargs):
            rv = func(inst, *args, **kwargs)
            self.registry.pop(inst, None)
            return rv
        return wrapper
    def invalidators(self, *funcs):
        return map(self.invalidator, funcs)

class BindingMix(MemoMix):
    __bound_desc__ = None
    def bind(self, desc):
        self.__bound_desc__ = desc
        return self
    def __get__(self, inst, cls):
        return (self if not inst else
            self.registry[inst] if inst in self.registry else
            self.registry.setdefault(inst,
                self.__by_func__(self.__bound_desc__.__get__(inst, type))))
