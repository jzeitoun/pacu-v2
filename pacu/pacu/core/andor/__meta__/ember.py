from pacu.core.andor.ctypes.library import ctypes_library as lib
from pacu.core.andor.instrument.system import SystemInstrument
from pacu.core.andor.instrument.zyla import ZylaInstrument

if lib.check(verbose=False):
    si = SystemInstrument()
    has_andor = True
    number_of_cameras = si.device_count
    camera_indice = range(si.device_count)

__all__ = [
    'has_andor',
    'number_of_cameras',
    'camera_indice'
]
