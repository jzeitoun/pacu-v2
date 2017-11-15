from pacu.core.svc.impl.component import Component
from pacu.core.svc.vstim.monitor.example_field import ExampleField
from pacu.core.svc.vstim.monitor.example_field_select import ExampleFieldSelect

class ExampleComponent(Component):
    package = __package__
    sui_icon = 'desktop'
    description = 'A detailed description about what it is, and how it works.'
    field1 = ExampleField('', title='Field')
    field2 = ExampleFieldSelect(None)
