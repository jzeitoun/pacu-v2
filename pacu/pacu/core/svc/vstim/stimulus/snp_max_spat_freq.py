from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPMaxSFrequency(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('')
    placeholder = EmberAttr('')
    title = EmberAttr('Max SFrequency')
    tip = EmberAttr('')
