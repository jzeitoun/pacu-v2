from __future__ import absolute_import

from pacu.core.andor.ctypes.handle import CTypesHandle
from pacu.core.andor.feature.base import BaseFeature
from pacu.util.prop.memoized import memoized_property

HANDLE_SYSTEM = 1

class BaseInstrument(object):
    def __init__(self, handle=HANDLE_SYSTEM):
        self.handle = CTypesHandle(handle)
    def release(self):
        self.handle.release()
    @memoized_property
    class meta(object):
        def __init__(self, inst):
            self.inst = inst
        @property
        def _attributes(self):
            return list(self.inst.feat)
        def __dir__(self):
            return self._attributes
        def __getattr__(self, key):
            if key in self._attributes:
                meta = self.inst.feat[key].get_meta(self.inst, key)
                setattr(self, key, meta)
                return meta
            raise AttributeError(key)
        def __iter__(self):
            for attr in self._attributes:
                yield getattr(self, attr).format_show()
        def __str__(self):
            return '\n\n'.join(self)
        __getitem__ = __getattr__
    feat = BaseFeature.descriptor_set()
