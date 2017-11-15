import importlib

from pacu.core.svc.impl.component import Component

def get(req, pkgname, clsname, spec, **kwargs):
    package = importlib.import_module(pkgname)
    cls = getattr(package, clsname)
    if not issubclass(cls, Component):
        raise TypeError('Not a service component')
    return format(cls(**kwargs), spec)

# generic_monitor = 'pacu.core.svc.vstim.monitor.generic'
# GenericMonitor = 'GenericMonitor'
# print get(None, generic_monitor, GenericMonitor, 'ember')
