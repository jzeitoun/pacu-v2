from __future__ import absolute_import
from __future__ import print_function

import inspect

from .get import clsname

def auto_strict(self):
    # TODO: it does not work well with a class where __init__ is not overridden
    spec = inspect.getargspec(self.__init__)
    keys = spec.args[1:]
    vals = [getattr(self, attr) for attr in keys]
    offset = len(keys) - len(spec.defaults or [])
    reprspec = ', '.join(
        (
            '%s=' % key if spec.defaults and offset <= index else ''
        ) + repr(val)
        for index, (key, val) in enumerate(zip(keys, vals))
    )
    return '{}({})'.format(clsname(self), reprspec)

def test():
    class Test1(object):
        def __init__(self, name, addr='nowhere'):
            self.name = name
            self.addr = addr
        __repr__ = auto_strict
    class Test2(object):
        def __init__(self, lang='ko'):
            self.lang = lang
        __repr__ = auto_strict
    class Test3(object):
        def __init__(self, ref):
            self.ref = ref
        __repr__ = auto_strict
    print(Test1('HT', 708))
    print(Test2('en'))
    print(Test3(inspect))
