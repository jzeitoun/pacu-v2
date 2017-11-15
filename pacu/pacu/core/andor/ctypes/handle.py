import atexit
from functools import partial

from pacu.core.andor.error import ZylaError
from pacu.core.andor.ctypes.define import AT_64, AT_STRING, AT_H, AT_DOUBLE, AT_BOOL
from pacu.core.andor.ctypes.library import ctypes, ctypes_library
from pacu.util.compat import str

core = ctypes_library.atcore
util = ctypes_library.atutility

def describe(apiname, CTYPE, verb=None):
    def getset(self, feature, value=None, T=CTYPE):
        verb, box, ref = ('Get', T(), True) if value is None else ('Set', T(value), False)
        return self.do(verb, apiname, feature, box, ref)
    def do(self, feature):
        return self.do(verb, apiname, feature, CTYPE(), True)
    return do if verb else getset

class CTypesHandle(int):
    # release = core.AT_Close
    @classmethod
    def acquire(cls, index=0):
        handle = AT_H()
        error = core.AT_Open(index, ctypes.byref(handle))
        if error:
            raise ZylaError(error)
        atexit.register(partial(core.AT_Close, handle.value))
        return handle.value
    def release(self):
        self.check_error(core.AT_Close(self))
    def check_error(self, error, retval=None):
        if error:
            raise ZylaError(error)
        return retval
    def core(self, apiname, *args):
        api = getattr(core, 'AT_%s' % apiname)
        error = api(self, *args)
        return self.check_error(error)
    def util(self, apiname, *args):
        api = getattr(util, 'AT_%s' % apiname)
        error = api(*args)
        return self.check_error(error)
    def do(self, verb, apiname, feature, box, ref, *args):
        api = getattr(core, 'AT_%s%s' % (verb, apiname))
        error = api(self, str.unsure(feature), ctypes.byref(box) if ref else box, *args)
        return self.check_error(error, box.value)
    def command(self, feature):
        error = core.AT_Command(self, str.unsure(feature))
        return self.check_error(error)
    def get_string(self, feature):
        length = self.get_string_max_length(feature)
        return self.do('Get', 'String', feature, AT_STRING(length), True, length)
    def get_enumstr(self, feature):
        box = AT_STRING(256)
        error = core.AT_GetEnumStringByIndex(self, str.unsure(feature), self.enum(feature), box, 256)
        return self.check_error(error, box.value)
    def get_enums(self, feature):
        feature = str.unsure(feature)
        for index in range(self.get_enum_count(feature)):
            enumstr = AT_STRING(256)
            core.AT_GetEnumStringByIndex(self, feature, index, enumstr, 256)
            # available = AT_BOOL()
            # implemented = AT_BOOL()
            # core.AT_IsEnumIndexAvailable(self, feature, index, available)
            # core.AT_IsEnumIndexImplemented(self, feature, index, implemented)
            yield enumstr.value #, available.value, implemented.value

    int = describe('Int', AT_64)
    bool = describe('Bool', AT_BOOL)
    float = describe('Float', AT_DOUBLE)
    enum = describe('EnumIndex', AT_64)
    is_implemented = describe('Implemented', AT_BOOL, 'Is')
    is_readonly = describe('ReadOnly', AT_BOOL, 'Is')
    is_writable = describe('Writable', AT_BOOL, 'Is')
    is_readable = describe('Readable', AT_BOOL, 'Is')
    get_int_max = describe('IntMax', AT_64, 'Get')
    get_int_min = describe('IntMin', AT_64, 'Get')
    get_float_max = describe('FloatMax', AT_DOUBLE, 'Get')
    get_float_min = describe('FloatMax', AT_DOUBLE, 'Get')
    get_string_max_length = describe('StringMaxLength', AT_64, 'Get')
    get_enum_count = describe('EnumCount', AT_64, 'Get')
