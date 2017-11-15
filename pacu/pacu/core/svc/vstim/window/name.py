from pacu.util.spec.str import StringSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Name(PacuAttr, StringSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('description for name')
    placeholder = EmberAttr('place for name')
    title = EmberAttr('Name')
    tooltip = EmberAttr('tooltip for name')
