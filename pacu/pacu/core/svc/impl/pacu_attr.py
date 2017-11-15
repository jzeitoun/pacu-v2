from collections import OrderedDict
from pacu.util.compat.iterable import dict
from pacu.util.newtype.incremental_hash import IncrementalHash
from pacu.core.svc.impl.ember_attr import EmberAttr

class PacuAttr(IncrementalHash):
    embers = EmberAttr.descriptor_set()
    component = 'x-svc-comp-input-text'
    def get_ember_meta(self, inst, type):
        val = self.__get__(inst, type) # triggers __key__ set
        return dict(
            key = self.__key__,
            val = val,
            component = self.component,
            attrs=OrderedDict(self.embers.items()))
    def __set__(self, inst, value):
        try:
            super(PacuAttr, self).__set__(inst, value)
        except Exception as e:
            msg = ('Unable to set an attribute '
                '`{title}` of `{owner}`.({reason!s})').format(
                title=self.title, owner=type(inst).__name__, reason=e)
            raise Exception(msg)
