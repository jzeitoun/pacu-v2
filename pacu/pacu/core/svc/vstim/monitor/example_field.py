from pacu.util.spec.str import StringSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class ExampleField(PacuAttr, StringSpec):
    component = 'x-svc-comp-input-text'
    title = EmberAttr('Title')
    description = EmberAttr('A short description')
    placeholder = EmberAttr('A placeholder in case there\'s no input.')
    tooltip = EmberAttr('More tips for this field, regarding the value.')
