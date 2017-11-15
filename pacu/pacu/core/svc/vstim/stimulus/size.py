from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Size(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('number in deg')
    placeholder = EmberAttr('')
    title = EmberAttr('Size')
    tooltip = EmberAttr('')
