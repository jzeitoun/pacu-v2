from .base import DelegatorBase

class DescriptorDelegator(DelegatorBase):
    def __call__(self, attrs, key):
        return attrs[key]
