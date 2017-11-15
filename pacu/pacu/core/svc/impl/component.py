from pacu.util.compat.iterable import dict
from pacu.util.inspect.get import clsname
from pacu.core.svc.impl.pacu_attr import PacuAttr

class Component(object):
    description = 'Simple description goes here.'
    sui_icon = 'desktop'
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
    def __format__(self, spec):
        return self.as_ember_format.json if spec == 'ember' else super(
            Component, self).__format__(spec)
    @property
    def as_ember_format(self):
        return dict(
            clsname=clsname(self),
            pkgname=self.package,
            description = self.description,
            sui_icon = self.sui_icon,
            fields=self.pacus.map.get_ember_meta()
        )
    pacus = PacuAttr.descriptor_set()
