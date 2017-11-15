from .common import cstr

class str(cstr, unicode):
    @classmethod
    def unsure(cls, string): # should take care of encoding
        return cls(string)
