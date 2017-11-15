from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Height(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('viewable screen (cm)')
    placeholder = EmberAttr('place for height')
    title = EmberAttr('Height')
    tooltip = EmberAttr('tooltip for height')
