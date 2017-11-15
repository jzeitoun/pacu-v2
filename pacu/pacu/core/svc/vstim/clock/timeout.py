from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Timeout(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('how long?')
    placeholder = EmberAttr('timeout')
    title = EmberAttr('Timeout')
    tooltip = EmberAttr('second..')
