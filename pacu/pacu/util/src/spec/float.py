from .base import BaseSpec
from .validator import is_positive
from .validator import is_zpositive

class FloatSpec(BaseSpec):
    coercer = float
class PositiveFloatSpec(FloatSpec):
    validator = is_positive
class ZPositiveFloatSpec(FloatSpec):
    validator = is_zpositive
