from .base import DelegatorBase

class EachDelegator(DelegatorBase):
    def __dir__(self):
        return [
            key for key in dir(self.proxy._ptype)
            if not key.startswith('_')
               and not callable(getattr(self.proxy._ptype, key))]
    def __call__(self, attrs, key):
        return [
            getattr(prop, key)
            for prop in attrs.values()]
    def __iter__(self):
        return iter(
            zip(*map(self.__getattr__, dir(self)))
        )
