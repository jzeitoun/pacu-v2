# from pacu.util.spec.float import ZPositiveFloatSpec
# from pacu.core.svc.impl.pacu_attr import PacuAttr
# from pacu.core.svc.impl.ember_attr import EmberAttr

from pacu.util.spec.enum import EnumSpec
from pacu.util.spec.enum import EnumItem
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

rotations = [
    EnumItem('0', name='0', sui_icon='clock'),
    EnumItem('90', name='90', sui_icon='clock'),
    EnumItem('180', name='180', sui_icon='clock'),
    EnumItem('270', name='270', sui_icon='clock'),
]

class SNPRotation(EnumSpec, PacuAttr):
    component = 'x-svc-comp-input-select'
    description = EmberAttr('')
    placeholder = EmberAttr('0 for vertical, 90 for horizontal')
    title = EmberAttr('Rotation')
    # tooltip = EmberAttr('')
    items = EmberAttr(rotations)

# class SNPRotation(PacuAttr, ZPositiveFloatSpec):
#     component = 'x-svc-comp-input-text'
#     description = EmberAttr('')
#     placeholder = EmberAttr('')
#     title = EmberAttr('Rotation')
#     tip = EmberAttr('')
