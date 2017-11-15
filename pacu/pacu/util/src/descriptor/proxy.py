from ..inspect.get import agg_public_types
from ..prop.memoized import MemoizedProperty
from .delegator.key import KeyDelegator
from .delegator.value import ValueDelegator
from .delegator.desc import DescriptorDelegator
from .delegator.map import MapDelegator
from .delegator.each import EachDelegator

class DescriptorProxy(object):
    def __init__(self, inst, ptype, attrs=()):
        self._cls = inst.__class__
        self._inst = inst
        self._ptype = ptype
        self._attrs = agg_public_types(type(inst), ptype, attrs)
    def __iter__(self):
        return iter(self.key)
    def __getitem__(self, prop_attr): # rough implementation
        if isinstance(prop_attr, int):
            raise Exception('Wrong type to call proxy.')
        elif isinstance(prop_attr, tuple):
            return [getattr(self.desc, pattr) for pattr in prop_attr]
            # return zip(*[
            #     [getattr(desc, pattr) for desc in self.desc]
            #     for pattr in prop_attr])
        else:
            return getattr(self.desc, prop_attr)
            # return [getattr(desc, prop_attr) for desc in self.desc]
    def zip(self, *ds):
        return zip(*[
            iter(getattr(self, delegator))
            for delegator in ds])
    def items(self):
        return self.zip('key', 'val')
    key = MemoizedProperty(KeyDelegator)
    val = MemoizedProperty(ValueDelegator)
    desc = MemoizedProperty(DescriptorDelegator)
    map = MemoizedProperty(MapDelegator)
    each = MemoizedProperty(EachDelegator)
