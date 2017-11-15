from pacu.core.andor.feature.base import BaseFeature, AbstractMeta

class IntMeta(AbstractMeta):
    @property
    def range(self):
        return self.min_int, self.max_int
    coercer = int

class IntFeature(BaseFeature):
    Meta = IntMeta
    def __get__(self, inst, type):
        return inst.handle.int(self.feature) if inst else self
    def __set__(self, inst, val):
        inst.handle.int(self.feature, val)
