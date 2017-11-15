from pacu.util.spec.list import PositiveFloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class TFrequencies(PacuAttr, PositiveFloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('description for tfreq')
    placeholder = EmberAttr('place for tfreq')
    title = EmberAttr('Temporal Frequencies')
    tooltip = EmberAttr('tooltip for tfreq')
