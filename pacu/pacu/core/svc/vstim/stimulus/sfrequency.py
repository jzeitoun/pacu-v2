from pacu.util.spec.float import ZPositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SFrequency(PacuAttr, ZPositiveFloatSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('description for sfreq')
    placeholder = EmberAttr('place for sfreq')
    title = EmberAttr('Spatial Frequency')
