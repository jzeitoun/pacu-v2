from pacu.util.spec.list import FloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class PositionTuple(PacuAttr, FloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('2 floats in deg')
    placeholder = EmberAttr('')
    title = EmberAttr('Position')
    tooltip = EmberAttr('')
