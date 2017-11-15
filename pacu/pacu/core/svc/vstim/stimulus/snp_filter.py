from pacu.util.spec.enum import EnumSpec
from pacu.util.spec.enum import EnumItem
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

rotations = [
    EnumItem('Gaussian', name='Gaussian', sui_icon='cube'),
    EnumItem('Square', name='Square', sui_icon='cube'),
]

class SNPFilter(EnumSpec, PacuAttr):
    component = 'x-svc-comp-input-select'
    description = EmberAttr('')
    placeholder = EmberAttr('Square for debug purpose')
    title = EmberAttr('Filter')
    items = EmberAttr(rotations)
