from pacu.core.andor.ctypes.library import ctypes

AT_64 = ctypes.c_int64
AT_H = ctypes.c_int
AT_BOOL = ctypes.c_int
AT_U8 = ctypes.c_ubyte
AT_U8P = ctypes.POINTER(ctypes.c_ubyte)
AT_WC = unicode

AT_INFINITE = 0xFFFFFFFF
AT_CALLBACK_SUCCESS = 0
AT_TRUE = 1
AT_FALSE = 0
AT_HANDLE_UNINITIALISED = -1
AT_HANDLE_SYSTEM = 1

# extended type
AT_DOUBLE = ctypes.c_double
AT_INT = ctypes.c_int
def AT_STRING(length=None):
    return (ctypes.c_wchar*length)(
    ) if length else (ctypes.POINTER(ctypes.c_wchar)())
