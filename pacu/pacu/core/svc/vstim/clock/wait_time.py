from pacu.util.spec.int import ZPositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class WaitTime(PacuAttr, ZPositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('After synchronization')
    placeholder = EmberAttr('ex) 0')
    title = EmberAttr('Wait Time')
    tooltip = EmberAttr('tooltip for wait time')
