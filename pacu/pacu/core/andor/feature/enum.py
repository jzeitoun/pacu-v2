from pacu.core.andor.feature.base import BaseFeature, AbstractMeta

class EnumishInt(int):
    name = None
    @classmethod
    def make(cls, number, string=''):
        self = cls(number)
        self.name = string
        return self
    def __repr__(self):
        return self.name if self.name else super(EnumishInt, self).__repr__()
    def __str__(self):
        return self.name if self.name else super(EnumishInt, self).__str__()

class EnumMeta(AbstractMeta):
    @property
    def range(self):
        return self.enums
    coercer = int

class EnumFeature(BaseFeature):
    Meta = EnumMeta
    def __get__(self, inst, type):
        if inst:
            enumint = inst.handle.enum(self.feature)
            enumstr = inst.handle.get_enumstr(self.feature)
            return EnumishInt.make(enumint, enumstr)
        return self
    def __set__(self, inst, val):
        inst.handle.enum(self.feature, val)
