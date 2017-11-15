from pacu.util.spec.float import PositiveFloatSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class Contrast(PacuAttr, PositiveFloatSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('NO LONGER USED')
    placeholder = EmberAttr('')
    title = EmberAttr('Contrast (DEPRECATED)')
    tooltip = EmberAttr('Please use `Contrasts` field instead.')
