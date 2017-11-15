from pacu.util.spec.int import ZPositiveIntSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SNPContrThreshold(PacuAttr, ZPositiveIntSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('0~100%')
    placeholder = EmberAttr('')
    title = EmberAttr('Contrast Threshold')
    tooltip = EmberAttr('Setup to have B/W blobs. (0 will do nothing.)')
