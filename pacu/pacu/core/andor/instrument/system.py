from __future__ import absolute_import

from pacu.core.andor.instrument.base import BaseInstrument
from pacu.core.andor.feature.string import StringFeature
from pacu.core.andor.feature.int import IntFeature
from pacu.core.andor.feature.base import BaseFeature
from pacu.util.prop.memoized import memoized_property

class SystemInstrument(BaseInstrument):
    software_version = StringFeature('SoftwareVersion')
    device_count = IntFeature('DeviceCount')
    def acquire(self, Instrument, index=0):
        return Instrument(self.handle.acquire(index))
    feat = BaseFeature.descriptor_set()
