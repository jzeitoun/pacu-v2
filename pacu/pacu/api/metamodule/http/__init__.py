import sys
import importlib

def get(req, pkgname, spec): # spec is most likely 'ember'
    pkgname = '{}.__meta__.{}'.format(pkgname, spec)
    sys.modules.pop(pkgname, None)
    # can introduce import error
    package = importlib.import_module(pkgname)
    try:
         __all__ = package.__all__
    except Exception as e:
        __all__ = []
        print 'metamodule should define __all__ attribute'
        print e
    return {key: getattr(package, key, None) for key in __all__}
