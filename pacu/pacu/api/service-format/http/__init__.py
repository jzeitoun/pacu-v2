import importlib

from pacu.core.svc.impl import specs

def get(req, pkgname, spec): # spec is most likely 'ember'
    package = importlib.import_module(pkgname)
    __spec__ = package.__all__
    if not isinstance(__spec__, specs):
        raise TypeError('Not a service spec')
    return format(__spec__, spec)

# vstim = 'pacu.core.svc.vstim'
# print get(None, vstim, 'ember')
