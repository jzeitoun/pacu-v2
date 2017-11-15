from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Dist(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('description for dist')
    placeholder = EmberAttr('place for dist')
    title = EmberAttr('Distance')
    tooltip = EmberAttr('tooltip for dist')
