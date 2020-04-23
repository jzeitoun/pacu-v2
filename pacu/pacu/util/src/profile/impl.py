import os
import types
import importlib
from collections import OrderedDict

from .proxy import SectionProxy
from .config import SaferConfigParser
from .. import logging
from .. import identity
from ..identity import environ
from ..prop.memoized import memoized_property
from ..inspect import repr
from ..str.poly import polymorphicStr
from ..module.mock import MockModule


user_profile_path = identity.path.userenv.joinpath('profile')

class MockCompanion(MockModule):
    def default(self, *args, **kwargs):
        return NotImplemented

class Profile(object):
    def __init__(self, path, package, name, overrider=None, current=None):
        self.path = path
        self.package = package
        self.name = name
        self.overrider = overrider or {}
        self.current = current
    def __iter__(self):
        for name in self.sections():
            yield self.section(name)
    __repr__ = repr.auto_strict
    @memoized_property
    def builtin(self):
        return self.path.joinpath(self.name).with_suffix('.cfg')
    @memoized_property
    def user(self):
        return user_profile_path.joinpath(self.name).with_suffix('.cfg')
    @memoized_property
    def config(self):
        return SaferConfigParser.from_filenames(self.builtin.str, self.user.str)
    @memoized_property
    def py(self):
        try: # should validate?
            module = importlib.import_module('.' + self.name, self.package)
            module.default # check if it has `default` at least.
            return module
        except Exception as e:
            l = logging.get_default()
            l.error(
                'An error occurred in creating profile `{}`.'.format(self.name))
            l.error(str(type(e)))
            l.error(str(e))
            return MockCompanion()
    def sections(self):
        return self.config.sections()
    def section(self, section):
        config = self.config
        kvs = [(option, polymorphicStr(config.get(section, option)))
                for option in config.options(section)]
        overrider = {key: polymorphicStr(val)
                for key, val in list(self.overrider.items())}
        proxy = SectionProxy(section, OrderedDict(kvs, **overrider))
        companion = self.py # companion
        init = getattr(companion, section, None) or companion.default
        proxy.__call__ = types.MethodType(init, proxy, SectionProxy)
        return proxy
    @property
    def first_name(self):
        try: # returns a profile that was defined firstly.
            return self.config.sections()[0]
        except:
            pass
    @property
    def first(self):
        first_name = self.first_name
        if first_name:
            return self.section(first_name)
    @property
    def environ(self): # from environment variables
        val = environ.getval('profile', self.name)
        if val:
            try:
                return self.section(val)
            except:
                print(('env profile', val, 'seems not working.'))
    _current = None
    @property
    def current(self):
        if self._current:
            try:
                return self.section(self._current)
            except:
                print(('env profile', self._current, 'seems not working.'))
    @current.setter
    def current(self, val):
        self._current = val # validation required
    @property
    def as_resolved(self):
        return self.current or self.environ or self.first
    _inst = None
    def instance(self, *args, **kwargs):
        if not self._inst:
            resolved = self.as_resolved
            if resolved:
                self._inst = resolved(*args, **kwargs)
        return self._inst
    @property
    def name_as_resolved(self):
        return self._current or environ.getval('profile', self.name) or self.first_name
    @property
    def is_empty(self):
        return not bool(self.config.sections())
    def vim(self):
        if self.user.is_file():
            cmd = 'vim %s' % self.user.str
        else:
            cmd = 'echo "%s" | vim - +"file %s" +"set filetype=cfg"' % (
                self.blueprint, self.user.str)
        os.system(cmd)
    def remove(self):
        os.remove(self.user.str)
    def reset(self):
        self.user.write(str(self.blueprint), mode='w')
    @property
    def blueprint(self):
        return '\n'.join(
            '[%s]' % s for s in self.sections())
