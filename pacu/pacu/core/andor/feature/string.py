from pacu.core.andor.feature.base import BaseFeature, AbstractMeta

NOT_YET = 'Setting a value on string feature is not supported at this time.'

class StringMeta(AbstractMeta):
    @property
    def range(self):
        return 0, self.max_string_length
    coercer = str

class StringFeature(BaseFeature):
    Meta = StringMeta
    def __get__(self, inst, type):
        return inst.handle.get_string(self.feature) if inst else self
    def __set__(self, inst, val):
        raise Exception(NOT_YET)
