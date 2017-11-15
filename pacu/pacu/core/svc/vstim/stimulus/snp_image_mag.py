from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPImageMag(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('Image magnification factor')
    placeholder = EmberAttr('integer')
    title = EmberAttr('ImageMag')
    tooltip = EmberAttr('This number determines size of movie. (Dimension of monitor pixels divided by this number.)')
