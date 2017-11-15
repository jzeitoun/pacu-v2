from pacu.util.spec.list import PositiveFloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SFrequencies(PacuAttr, PositiveFloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('floating numbers')
    placeholder = EmberAttr('place for sfreq')
    title = EmberAttr('Spatial Frequencies')
    tooltip = EmberAttr('tooltip for sfreq')
