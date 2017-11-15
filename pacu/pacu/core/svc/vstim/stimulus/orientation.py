from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Orientation(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('description for orientation')
    placeholder = EmberAttr('place for orientation')
    title = EmberAttr('Orientation')
