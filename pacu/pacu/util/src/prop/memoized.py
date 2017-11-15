from functools import wraps
from weakref import WeakKeyDictionary

class MemoizedProperty(object):
    def __init__(self, getter):
        self.getter = getter
        self.registry = WeakKeyDictionary()
    def __get__(self, inst, cls):
        return (self if not inst else
                self.registry[inst] if inst in self.registry else
                self.registry.setdefault(inst, self.getter(inst)))
    def __set__(self, inst, value):
        self.registry[inst] = value
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

memoized_property = MemoizedProperty
