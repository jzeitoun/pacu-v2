from pacu.util.spec.enum import EnumSpec
from pacu.util.spec.enum import EnumItem
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

people = [
    EnumItem('anonymous', name='Anonymous', sui_icon='spy'),
    EnumItem('dario', name='Dario', sui_icon='user'),
    EnumItem('melissa', name='Melissa', sui_icon='user'),
    EnumItem('kirstie', name='Kirstie', sui_icon='user'),
    EnumItem('jack', name='Jack', sui_icon='user'),
    EnumItem('xiao', name='Xiao', sui_icon='user'),
    EnumItem('carey', name='Carey', sui_icon='user'),
    EnumItem('xulab', name='Xu Lab', sui_icon='user'),
]

class ExpBy(EnumSpec, PacuAttr):
    component = 'x-svc-comp-input-select'
    description = EmberAttr('string')
    placeholder = EmberAttr('')
    title = EmberAttr('Experimenter')
    items = EmberAttr(people)
    tooltip = EmberAttr('Who is arranging this session?')
