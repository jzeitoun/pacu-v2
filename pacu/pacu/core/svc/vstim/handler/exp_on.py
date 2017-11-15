from pacu.util.spec.enum import EnumSpec
from pacu.util.spec.enum import EnumItem
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

gears = [
    EnumItem('pilot', name='Pilot', sui_icon='plane'),
    # EnumItem('2p', name='2P', sui_icon='database'),
    EnumItem('intrinsic', name='Intrinsic', sui_icon='database'),
    EnumItem('scanbox', name='Scanbox', sui_icon='database'),
    EnumItem('miniscope', name='Miniscope', sui_icon='database')
]

class ExpOn(EnumSpec, PacuAttr):
    component = 'x-svc-comp-input-select'
    description = EmberAttr('string')
    placeholder = EmberAttr('select...')
    title = EmberAttr('Gear')
    items = EmberAttr(gears)
    tooltip = EmberAttr('')
