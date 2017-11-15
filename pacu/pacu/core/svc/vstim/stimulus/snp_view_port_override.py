from pacu.util.spec.list import PositiveFloatListSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPViewPortOverride(PacuAttr, PositiveFloatListSpec):
    component = 'x-svc-comp-input-array'
    description = EmberAttr('Two numbers')
    placeholder = EmberAttr('0, 0')
    title = EmberAttr('View Port Override')
    tooltip = EmberAttr(
        'When you run a warped stimulus with too SHORT distance like 10 cm, '
        'visuals could be rendered off screen. This parameter overrides '
        'the extent of view port. Setting `0, 0` skips override.'
        'By default, view port is set the same dimension of monitor.'
    )
