from pacu.util.spec.bool import BoolSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Randomize(PacuAttr, BoolSpec):
    component = 'x-svc-comp-input-check'
    description = EmberAttr('boolean')
    title = EmberAttr('Randomize')
