from .base import DelegatorBase

class ValueDelegator(DelegatorBase):
    def __call__(self, attrs, key):
        descriptor = attrs[key]
        inst = self.proxy._inst
        cls = self.proxy._cls
        return descriptor.__get__(inst, cls)
