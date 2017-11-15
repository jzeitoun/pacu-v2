from pacu.util.spec.int import ZPositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Pin(PacuAttr, ZPositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('Signal will emit on this pin number.')
    placeholder = EmberAttr('ex) 0')
    title = EmberAttr('Pin Number')
    tooltip = EmberAttr('tooltiptime')
