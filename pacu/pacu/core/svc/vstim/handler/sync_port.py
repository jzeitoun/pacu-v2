from pacu.util.spec.str import StringSpec
from pacu.core.svc.impl.pacu_attr import PacuAttr
from pacu.core.svc.impl.ember_attr import EmberAttr

class SyncPort(PacuAttr, StringSpec):
    component = 'x-svc-comp-input-text'
    description = EmberAttr('For another PACU with Camera')
    placeholder = EmberAttr('...')
    title = EmberAttr('Port Number')
    tooltip = EmberAttr('Usually it is 8761.')
