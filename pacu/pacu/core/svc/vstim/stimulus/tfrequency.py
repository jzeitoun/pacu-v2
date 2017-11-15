from pacu.util.spec.float import ZPositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class TFrequency(PacuAttr, ZPositiveFloatSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('description for tfreq')
    placeholder = EmberAttr('place for tfreq')
    title = EmberAttr('Temporal Frequency')
