from pacu.util.spec.list import PositiveFloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Orientations(PacuAttr, PositiveFloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('floating numbers')
    placeholder = EmberAttr('place for orientations')
    title = EmberAttr('Orientations')
    tooltip = EmberAttr('tooltip for orientations')
