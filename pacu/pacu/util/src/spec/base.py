from weakref import WeakKeyDictionary
from ..newtype.incremental_hash import IncrementalHash

class BaseSpec(IncrementalHash):
    coercer = None
    validator = None
    transformer = None
    def __init__(self, default, **kwargs):
        self.registry = WeakKeyDictionary()
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.default = default
    def __get__(self, inst, type):
        return (self if not inst else
                self.registry[inst] if inst in self.registry else
                self.default)
    def __set__(self, inst, value):
        self.registry[inst] = self.transform(self.validate(self.coerce(value)))
    @property
    def default(self):
        return self._default
    @default.setter
    def default(self, value):
        self._default = self.transform(self.validate(self.coerce(value)))
    def coerce(self, value): # ValueError, TypeError could raise
        return self.coercer(value) if self.coercer else value
    def validate(self, value):
        if self.validator:
            error = self.validator(value)
            if error:
                raise ValueError(error)
        return value
    def transform(self, value):
        return self.transformer(value) if self.transformer else value
