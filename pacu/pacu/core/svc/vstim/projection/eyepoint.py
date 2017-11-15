from pacu.util.spec.float import ZPositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Eyepoint(PacuAttr, ZPositiveFloatSpec):
    component = 'x-svc-comp-input-text'

class EyepointX(PacuAttr, ZPositiveFloatSpec):
    description = EmberAttr('description for eyepoint x')
    placeholder = EmberAttr('place for eyepoint x')
    title = EmberAttr('Eyepoint X')
    tooltip = EmberAttr('tooltip for eyepoint x')

class EyepointY(PacuAttr, ZPositiveFloatSpec):
    description = EmberAttr('description for eyepoint y')
    placeholder = EmberAttr('place for eyepoint y')
    title = EmberAttr('Eyepoint Y')
    tooltip = EmberAttr('tooltip for eyepoint y')
