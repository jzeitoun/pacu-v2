from pacu.util.spec.list import PositiveFloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Contrasts(PacuAttr, PositiveFloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('floating numbers')
    placeholder = EmberAttr('1.0')
    title = EmberAttr('Contrasts')
    tooltip = EmberAttr('You can have multiple contrasts.')
