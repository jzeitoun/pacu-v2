from __future__ import absolute_import

from pacu.core.andor.ctypes.library import ctypes

c_int = ctypes.c_int
c_wchar_p = ctypes.c_wchar_p
c_void_p = ctypes.c_void_p
try:
    c_feat_cb = ctypes.WINFUNCTYPE(c_int, c_int, c_wchar_p, c_void_p)
except:
    c_feat_cb = ctypes.PYFUNCTYPE(c_int, c_int, c_wchar_p, c_void_p)


def initialize(lib):
    enfunc = lib.AT_RegisterFeatureCallback
    enfunc.argtypes = [c_int, c_wchar_p, c_feat_cb, c_void_p]
    enfunc.restype = c_int

    defunc = lib.AT_UnregisterFeatureCallback
    defunc.argtypes = [c_int, c_wchar_p, c_feat_cb, c_void_p]
    defunc.restype = c_int
