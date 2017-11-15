from pacu.util.spec.enum import EnumSpec
from pacu.util.spec.enum import EnumItem
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

deg = EnumItem('deg', name='DEG')
cm = EnumItem('cm', name='CM')

class Unit(EnumSpec, PacuAttr):
    component = 'x-svc-comp-input-select'
    description = EmberAttr('description for unit')
    placeholder = EmberAttr('choose 1')
    title = EmberAttr('Width Unit')
    items = EmberAttr((deg, cm))
    tooltip = EmberAttr('tooltip for unit')
