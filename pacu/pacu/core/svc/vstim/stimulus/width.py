from pacu.util.spec.int import ZPositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Width(PacuAttr, ZPositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('degree')
    placeholder = EmberAttr('width of stimulus')
    title = EmberAttr('Width')
    tooltip = EmberAttr('0 for bypass')
