from .common import cstr

class str(cstr, str):
    @classmethod
    def unsure(cls, string):
        return string
