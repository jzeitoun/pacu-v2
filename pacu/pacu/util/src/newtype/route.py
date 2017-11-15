from collections import OrderedDict

from .impl import newtype

class chainSubscriptable(newtype):
    resolve = object
    def __init__(cls, name, bases, nmspc):
        super(chainSubscriptable, cls).__init__(name, bases, nmspc)
        cls.map = OrderedDict()
    def __missing__(cls, key, val=object):
        Route = cls.extend(val)
        cls.map[key] = Route
        return Route
    def __setitem__(cls, key, val):
        try:
            cls.map[key].resolve = val
        except KeyError:
            return cls.__missing__(key, val)
    def __getitem__(cls, key):
        try:
            return cls.map[key]
        except KeyError:
            return cls.__missing__(key)
    def __repr__(cls):
        return '{0.__name__} => {0.resolve.__name__}'.format(cls)
    def extend(cls, resolve=object):
        return chainSubscriptable(cls.__name__, (cls,), dict(resolve=resolve))

class Route(chainSubscriptable.base()):
    args = ()
    def __init__(self, *args):
        self.args = args
    def __getitem__(self, item):
        for candidate in type(item).mro():
            if candidate in self.map:
                args = self.args + (item,)
                Route = self.map[candidate]
                if Route.map:
                    return Route(*args)
                else:
                    return Route.resolve(*args)
        else:
            raise KeyError
"""
class AType(object): pass
class StrEx(str): pass
class Test1(object):
    def __init__(self, str, int, float):
        self.str = str
        self.int = int
        self.float = float
class Test2(object):
    def __init__(self, *args): pass
class Test3(Test2): pass
class Test4(Test3): pass
Route[str][int][float] = Test1
Route[StrEx][int][float] = Test2
Route[StrEx][int][AType] = Test3
Route[str][int][AType] = Test4
route = Route()
t1 = route['string'][14][123.134]
t2 = route[StrEx('extended!')][14][123.134]
t3 = route[StrEx('extended!')][14][AType()]
t4 = route['justastring'][14][AType()]
try:
    route[2586][14][AType()]
except KeyError:
    pass # should be raised
"""
