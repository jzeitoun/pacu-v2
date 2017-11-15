from .base import BaseSpec
from ..compat import str

class EnumSpec(BaseSpec):
    items = () # can be a type of string-like or EnumItem
    def __init__(self, default=None, **kwargs):
        super(EnumSpec, self).__init__(default, **kwargs)
    def coercer(self, val):
        if isinstance(val, str) and val.isdigit():
            return int(val)
        return val
    def validator(self, val):
        if val is None:
            pass
        elif isinstance(val, int):
            if val >= len(self.items):
                return 'Value `{}` is out of enum-range. ' \
                   'It should be less than {}'.format(val, len(self.items))
        elif val not in self.items:
            return 'Value `{}` is out of enum-range. ' \
                   'It should be one of {}'.format(val, map(str, self.items))
    def transformer(self, val):
        if isinstance(val, int):
            return val
        elif val is not None:
            return self.items.index(val)

class EnumItem(dict):
    def __new__(cls, __name__, **mapping):
        self = super(cls, EnumItem).__new__(cls, mapping)
        self.__name__ = __name__
        return self
    def __init__(self, __name__, **mapping):
        super(EnumItem, self).__init__(mapping)
    def __eq__(self, that):
        return self.__name__ == that
    def __repr__(self):
        repred = super(EnumItem, self).__repr__()
        return 'EnumItem({!r}, **{})'.format(self.__name__, repred)
    def __str__(self):
        return self.__name__
"""
item1 = EnumItem('deg', key='val')
item2 = EnumItem('cm', another='value')

class Unit(EnumSpec, PacuAttr):
    items = EmberAttr((item1, item2))
"""
