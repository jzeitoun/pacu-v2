from pacu.util.spec.str import StringSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class DestIP(PacuAttr, StringSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('IP Address')
    placeholder = EmberAttr('place for ip')
    title = EmberAttr('Destination IP')
    tooltip = EmberAttr('tooltip for ip')
