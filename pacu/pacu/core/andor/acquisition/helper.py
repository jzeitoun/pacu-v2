from __future__ import absolute_import

import numpy as np

from pacu.core.andor.ctypes.library import ctypes

def get_contigious(height, width, order='F'):
    array = np.zeros((width, height), dtype='ushort', order='F')
    return array, array.ctypes.data_as(ctypes.POINTER(ctypes.c_ushort))

def offset_pointer(pointer, offset, dtype=ctypes.c_uint32):
    return ctypes.cast(
        ctypes.byref(pointer, offset),
        ctypes.POINTER(dtype)
    ).contents.value
