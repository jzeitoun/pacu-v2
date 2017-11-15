from types import ListType, TupleType

from pacu.util.str.poly import polymorphicStr
from .base import BaseSpec

class FloatListSpec(BaseSpec):
    def coercer(self, value):
        try:
            if isinstance(value, (ListType, TupleType)):
                return [float(e) for e in value]
            return polymorphicStr(value).listof(float, delim=(
                ',' if ',' in value else ' '))
        except ValueError as e:
            raise ValueError(
                'Raised error during setting value: %s' % e)

class PositiveFloatListSpec(FloatListSpec):
    def validator(self, value):
        if any(x < 0 for x in value):
            return 'Each orientation should not be a negative value.'
