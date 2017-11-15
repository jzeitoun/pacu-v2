from pacu.util.spec.int import ZPositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Screen(PacuAttr, ZPositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('number')
    placeholder = EmberAttr('0')
    title = EmberAttr('Screen#')
    tooltip = EmberAttr('0 is for primary screen.')
