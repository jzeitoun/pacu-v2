from pacu.util.spec.float import FloatSpec
from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class OnDuration(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('second')
    placeholder = EmberAttr('place for on duration')
    title = EmberAttr('On Duration')
    tooltip = EmberAttr('tooltip for on duration')

class OffDuration(PacuAttr, FloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('second')
    placeholder = EmberAttr('place for off duration')
    title = EmberAttr('Off Duration')
    tooltip = EmberAttr('tooltip for off duration')
