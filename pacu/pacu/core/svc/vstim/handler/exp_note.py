from pacu.util.spec.str import StringSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class ExpNote(PacuAttr, StringSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('string')
    placeholder = EmberAttr('Shortdescription')
    title = EmberAttr('Experiment Note')
