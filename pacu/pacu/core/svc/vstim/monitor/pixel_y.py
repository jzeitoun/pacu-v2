from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class PixelY(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('description for pixely')
    placeholder = EmberAttr('place for pixely')
    title = EmberAttr('Pixels Y')
    tooltip = EmberAttr('tooltip for pixely')
