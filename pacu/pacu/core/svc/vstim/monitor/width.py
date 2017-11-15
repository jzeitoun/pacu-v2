from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Width(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('viewable screen (cm)')
    placeholder = EmberAttr('place for width')
    title = EmberAttr('Width')
    tooltip = EmberAttr('tooltip for width')
