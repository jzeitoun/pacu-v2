from pacu.util.spec.int import ZPositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPViewWidth(PacuAttr, ZPositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('degree, zero to off')
    placeholder = EmberAttr('integer')
    title = EmberAttr('ViewWidth')
    # tip = EmberAttr('')
