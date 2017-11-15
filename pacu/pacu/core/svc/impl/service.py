import importlib

from pacu.core.svc.impl.component_dependency import ComponentDependency

def load_component(pkgname, clsname, kwargs=None):
    pkg = importlib.import_module(pkgname)
    Component = getattr(pkg, clsname)
    return Component(**kwargs or {})

class Service(object):
    comps = ComponentDependency.descriptor_set()
    def __init__(self, **components):
        for key, val in components.items():
            setattr(self, key, val)
    @classmethod
    def from_payload(cls, **payload):
        return cls(**{cmpname: load_component(**pay)
            for cmpname, pay in payload.items()})
    @property
    def as_summarized(self):
        return {key: dict(val.pacus.items())
                for key, val in self.comps.items()}
    @property
    def as_payload(self):
        return {key: dict(
            pkgname=val.package,
            clsname=type(val).__name__,
            kwargs=dict(val.pacus.items())
        ) for key, val in self.comps.items()}
    def __call__(self):
        return {}
