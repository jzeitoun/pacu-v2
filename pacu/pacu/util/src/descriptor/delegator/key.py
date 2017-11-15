from .base import DelegatorBase

class KeyDelegator(DelegatorBase):
    def __call__(self, attrs, key):
        if key not in attrs.keys():
            raise KeyError
        return key
