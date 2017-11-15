from __future__ import absolute_import

import atexit

from pacu.util.path import Path
from pacu.util.newtype.incremental_hash import IncrementalHash

try:
    from ctypes import wintypes as ctypes
    from ctypes import windll as cdll
    lib_basepath = Path.here('win')
except:
    import ctypes
    from ctypes import cdll
    lib_basepath = Path.here('linux')

class CDLLDescriptor(IncrementalHash):
    dll = None
    def __get__(self, inst, type):
        return self.dll if inst else self
    def __key_set__(self, key):
        try:
            self.dll = cdll.LoadLibrary(lib_basepath.joinpath(key).str)
        except OSError as e:
            print 'CDLL OSError:', e
            self.dll = NotImplemented
        return key

ERRORMSG = 'Error loading Andor device. (Library could not be initialized.)'

class CTypesLibrary(object):
    libs = CDLLDescriptor.descriptor_set()
    def check(self, verbose=True):
        try:
            kvs = self.libs.items()
            for key, value in kvs:
                if value is NotImplemented:
                    return False
        except Exception as e:
            if verbose:
                print ERRORMSG, '\n', type(e), e
            return False
        else:
            if verbose:
                maxlen = max(map(len, list(self.libs.key)))
                for name, dll in kvs:
                    print '{:{}}: {!r}'.format(name, maxlen, dll)
            return True

for key in ['atblkbx', 'atcl_bitflow', 'atcore', 'atdevregcam',
            'atspooler', 'atusb_libusb', 'atutility']:
    setattr(CTypesLibrary, key, CDLLDescriptor())

def release_handles(lib):
    def doit():
        print lib, 'release!'
        # for inst in ZylaBinding._instances:
        #     try:
        #         print 'closing handle %s...' % inst.handle
        #         inst.flush()
        #         inst.close(remove=False)
        #     except Exception as e:
        #         pass
    return doit

ctypes_library = CTypesLibrary()
if ctypes_library.check():
    ctypes_library.atcore.AT_InitialiseLibrary()
    ctypes_library.atutility.AT_InitialiseUtilityLibrary()
    atexit.register(release_handles(ctypes_library))
    atexit.register(ctypes_library.atcore.AT_FinaliseLibrary)
    atexit.register(ctypes_library.atutility.AT_FinaliseUtilityLibrary)
