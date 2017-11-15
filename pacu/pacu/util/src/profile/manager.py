from __future__ import print_function

from collections import defaultdict

from . import argparse
from .impl import Profile
from ..path import Path
from ..inspect import repr

class ProfileManager(object):
    """
    from pacu.profile import manager
    print list(manager.get('db'))
    db = manager.get('db').section('memory')
    session = db()
    memory_session = manager.instance('db') # an instance of primary profile
    """
    def __init__(self, path, package):
        self.path = Path.absdir(path)
        self.package = package
        self.overrider = defaultdict(dict)
        self.currents = {}
        self.registry = {}
    __repr__ = repr.auto_strict
    def instances(self, *names):
        return [Profile.instance() for Profile in map(self.get, names)]
    def instance(self, name):
        return self.get(name).instance()
    def getall(self, *names):
        return map(self.get, names)
    def get(self, name):
        if name in self.registry:
            return self.registry[name]
        profile = Profile(self.path, self.package, name,
            overrider = self.overrider[name],
            current = self.currents.get(name)
        )
        self.registry[name] = profile
        return profile
    def keys(self):
        return [item.stem for item in self.path.ls('*.cfg')]
    def values(self):
        return [self.get(key) for key in self.keys()]
    def items(self):
        return zip(self.keys(), self.values())
    def parse_sys_argv(self, argv=None):
        for kwargs in argparse.parse_argv(argv=argv):
            self.override(**kwargs)
        return self
    def override(self, profile, key, val):
        self.overrider[profile][key] = val
    def print_override_state(self):
        profile_names = self.keys()
        for profile_name, ovdict in self.overrider.items():
            if profile_name in profile_names:
                for key in ovdict:
                    print('Argument `%s.%s` takes override...' % (
                        profile_name, key))
            else:
                for key in ovdict:
                    print('Argument `%s.%s` seems invalid option...' % (
                        profile_name, key))
    def print_resolve_state(self):
        state = [(profile.name, profile.name_as_resolved)
                for profile in self.values()]
        for profile_name, resolved_name in state:
            print('Profile `{}` is resolved as `{}`...'.format(
                    profile_name, resolved_name))
    def print_status(self):
        self.print_resolve_state()
        self.print_override_state()
