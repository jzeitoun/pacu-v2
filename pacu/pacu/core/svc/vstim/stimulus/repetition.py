from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Repetition(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('number')
    placeholder = EmberAttr('place for repetition')
    title = EmberAttr('Repetition')
    tooltip = EmberAttr('tooltip for repetition')
