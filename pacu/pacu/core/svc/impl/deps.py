from pacu.util.newtype.incremental_hash import IncrementalHashBase
from pacu.util.descriptor.mixin.memoization import weakkeySupport
from weakref import WeakKeyDictionary

class Dependency(weakkeySupport.base(IncrementalHashBase)):
    dep_on = None
    def __init__(self, Module):
        self.Module = Module
        self.children = []
    def __set__(self, inst, val):
        module = self.Module(val)
        module.svc = inst
        self.registry[inst] = module
        for child in self.children:
            child.registry.pop(inst, None)
    def __get__(self, inst, cls):
        if inst not in self.registry:
            if self.dep_on:
                try:
                    dep, attr = self.dep_on
                    dep_module = dep.registry.get(inst)
                    if not dep_module:
                        return
                    attrs = attr.split('.')
                    value = reduce(getattr, attrs, dep_module)
                except Exception as e:
                    value = e
            else:
                value = None
            module = self.Module(value)
            module.svc = inst
            return self.registry.setdefault(inst, module)
        else:
            return self.registry.get(inst) if inst else self
    def on(self, dep, attr):
        self.dep_on = (dep, attr)
        dep.children.append(self)
        return self
    def __repr__(self):
        return '<{.__name__} => {.__name__}>'.format(self.__class__, self.Module)
