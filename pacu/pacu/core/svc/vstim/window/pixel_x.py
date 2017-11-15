from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class PixelX(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('description for pixelx')
    placeholder = EmberAttr('place for pixelx')
    title = EmberAttr('Pixels X')
    tooltip = EmberAttr('tooltip for pixelx')
