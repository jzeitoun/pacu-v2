from .base import BaseSpec
from .validator import is_positive
from .validator import is_zpositive

class IntSpec(BaseSpec):
    coercer = int
class PositiveIntSpec(IntSpec):
    validator = is_positive
class ZPositiveIntSpec(IntSpec):
    validator = is_zpositive
