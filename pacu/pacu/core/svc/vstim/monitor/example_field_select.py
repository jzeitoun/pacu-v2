from pacu.util.spec.enum import EnumSpec
from pacu.util.spec.enum import EnumItem
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

i1 = EnumItem('item1', name='Item1')
i2 = EnumItem('item2', name='Item2')

class ExampleFieldSelect(EnumSpec, PacuAttr):
    component = 'x-svc-comp-input-select'
    description = EmberAttr('A short description')
    placeholder = EmberAttr('Prompt message...')
    title = EmberAttr('Select')
    items = EmberAttr((i1, i2))
    tooltip = EmberAttr('More tips for this field, regarding the value.')
