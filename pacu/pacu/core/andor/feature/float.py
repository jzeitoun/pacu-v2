from pacu.core.andor.feature.base import BaseFeature, AbstractMeta

class FloatMeta(AbstractMeta):
    @property
    def range(self):
        return self.min_float, self.max_float
    coercer = float

class FloatFeature(BaseFeature):
    Meta = FloatMeta
    def __get__(self, inst, type):
        return inst.handle.float(self.feature) if inst else self
    def __set__(self, inst, val):
        inst.handle.float(self.feature, val)
