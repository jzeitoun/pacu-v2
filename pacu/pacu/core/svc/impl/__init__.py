import importlib
from collections import OrderedDict

import ujson as json


class spec(str):
    def __new__(cls, s, plural, components):
        return super(spec, cls).__new__(cls, s)
    def __init__(self, s, plural, components):
        super(spec, self).__init__(s)
        self.plural = plural
        self.components = components
    def __iter__(self):
        return iter(self.components)

class specs(list):
    def __new__(cls, iterable, package='', service=None):
        return super(specs, cls).__new__(cls, iterable)
    def __init__(self, iterable, package='', service=None):
        super(specs, self).__init__(iterable)
        self.package = package
        self.service = service
    def to_structure(self):
        return OrderedDict([
            (spec.plural, [self.format_component(spec, cmpname, clsname)
                            for cmpname, clsname in spec])
            for spec in self
        ])
    def get_component(self, spec, cmpname, clsname):
        cmp_pkgname = '{}.{}.{}'.format(self.package, spec, cmpname)
        cmp_pkg = importlib.import_module(cmp_pkgname)
        Component = getattr(cmp_pkg, clsname)
        return Component
    def format_component(self, spec, cmpname, clsname):
        return self.get_component(spec, cmpname, clsname)().as_ember_format
    def __format__(self, spec):
        return json.dumps(self.as_ember_format) if spec == 'ember' else super(
            specs, self).__format__(spec)
    @property
    def as_ember_format(self):
        return self.to_structure()
