import importlib
from weakref import WeakKeyDictionary

from pacu.util.newtype.incremental_hash import IncrementalHash

class ComponentDependency(IncrementalHash):
    def __init__(self):
        self.registry = WeakKeyDictionary()
    def __get__(self, inst, type):
        return self if not inst else self.registry[inst]
    def __set__(self, inst, value): # value is component
        self.registry[inst] = value
