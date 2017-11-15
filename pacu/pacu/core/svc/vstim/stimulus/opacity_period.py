from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class OpacityPeriod(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('second')
    # placeholder = EmberAttr('')
    title = EmberAttr('Opacity Period')
    # tooltip = EmberAttr('')
