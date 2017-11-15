from pacu.util.spec.float import ZPositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class MaxContrast(PacuAttr, ZPositiveFloatSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('number')
    placeholder = EmberAttr('')
    title = EmberAttr('Max Contrast')
