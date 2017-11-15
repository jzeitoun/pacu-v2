from ...compat.iterable import list
from .base import DelegatorBase

class MapDelegator(DelegatorBase):
    def __dir__(self):
        return [
            key for key in dir(self.proxy._ptype)
            if not key.startswith('_')
               and callable(getattr(self.proxy._ptype, key))]
    def __call__(self, attrs, key):
        inst = self.proxy._inst
        cls = self.proxy._cls
        pfuncs = [
            getattr(prop, key)
            for prop in attrs.values()]
        return lambda *a, **kw: list([
            pfunc(inst, cls, *a, **kw) for pfunc in pfuncs
        ])
