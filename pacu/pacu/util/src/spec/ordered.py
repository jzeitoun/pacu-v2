from ..newtype.incremental_hash import IncrementalHash
from .base import BaseSpec

class OrderedSpec(BaseSpec, IncrementalHash):
    value = None
    def __set__(self, inst, value):
        self.registry[inst] = value
