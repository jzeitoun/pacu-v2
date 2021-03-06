from pacu.util.spec.int import PositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPImgSize(PacuAttr, PositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('')
    placeholder = EmberAttr('')
    title = EmberAttr('Image(Texture) Size')
    tip = EmberAttr('')
