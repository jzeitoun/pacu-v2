import re
import os
import sys
import functools
import importlib

# TODO: a simple introduction needed!

class ShortCuttingImporter(object):
    re_actual_name = re.compile('(%s)' % __package__)
    def __init__(self, *skip_hops):
        skip_package = '.'.join(skip_hops)
        self.actual_package_base = '.'.join((__package__, skip_package))
        self.get_actual_package = functools.partial(
            self.re_actual_name.sub, r'\1.%s' % skip_package)
    def find_module(self, name, path=None):
        if path and os.path.dirname(__file__) in path:
            if not name.startswith(self.actual_package_base):
                return self # invokes `self.load_module`
    def load_module(self, name):
        actual_name = self.get_actual_package(name)
        module = importlib.import_module(actual_name)
        module.__name__ = name
        module.__package__ = name
        sys.modules[name] = module
        return module

sys.meta_path.append(ShortCuttingImporter('src'))
