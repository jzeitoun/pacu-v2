from pacu.util.spec.list import PositiveFloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SizeTuple(PacuAttr, PositiveFloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('2 floats in deg')
    placeholder = EmberAttr('')
    title = EmberAttr('Size')
    tooltip = EmberAttr('')
