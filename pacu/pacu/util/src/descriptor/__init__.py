"""
from ..newtype.incremental_hash import IncrementalHash
from .set import DescriptorSet

class Field(IncrementalHash):
    def __get__(self, inst, type):
        return hash(self) if inst else self
class A(object):
    f1 = Field()
    f2 = Field()
    fs = DescriptorSet(Field)
"""
