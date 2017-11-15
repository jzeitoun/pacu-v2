from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Port(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('port number')
    placeholder = EmberAttr('port number')
    title = EmberAttr('Port')
    tooltip = EmberAttr('1-65535')
