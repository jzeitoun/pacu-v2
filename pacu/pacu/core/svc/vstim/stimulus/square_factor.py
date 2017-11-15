from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SquareFactor(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('number')
    placeholder = EmberAttr('')
    title = EmberAttr('Square Factor')
    tooltip = EmberAttr('NxN number of squares will be rendered.')
