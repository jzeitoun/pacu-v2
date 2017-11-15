from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPDim(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('Image size')
    placeholder = EmberAttr('pixel')
    title = EmberAttr('Dim')
    tip = EmberAttr('in degree')
