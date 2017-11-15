from pandas import json
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR

from pacu.util.descriptor.mixin.memoization import MemoMix
from pacu.ext.sqlalchemy.types.mutable import MutableDict

class Variant(MemoMix):
    def __init__(self, default):
        self.default = default
    def __get__(self, inst, cls):
        return (self if not inst
           else self.registry[inst] if inst in self.registry
           else self.default)

class VariantBaseType(TypeDecorator):
    """
    Column('variant', MutableDict.as_mutable(ConcreteVariant))
    # or
    Column('variant', ConcreteVariant.as_mutable())
    """
    impl = VARCHAR
    @classmethod
    def as_mutable(cls):
        return MutableDict.as_mutable(cls)
    def process_bind_param(self, value, dialect): # From Python to DB
        if value is None:
            value = dict(self.variants.items())
        return json.dumps(value)
    def process_result_value(self, value, dialect): # From DB to Python
        try:
            data = json.loads(value)
        except Exception as e:
            data = {}
        # taking care of empty data to default variants
        return dict(dict(self.variants.items()), **data)
    variants = Variant.descriptor_set()
