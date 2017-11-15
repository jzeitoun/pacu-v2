from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Gamma(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    title = EmberAttr('Gamma')
    description = EmberAttr('description for gamma')
    placeholder = EmberAttr('A placeholder when there is no input')
    tooltip = EmberAttr('Tips for example or extra information')
