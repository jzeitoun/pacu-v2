import inspect
from functools import wraps

from ..inspect.get import fumble_key_by_val

class incrementalHashType(type):
    def __new__(mcl, name, bases, nmspc):
        if name == 'IncrementalHashBase': # so that class does not have them
            mcl.hashdict = {}
            mcl.counter = 0
            def __hash__(self):
                return mcl.hashdict[object.__hash__(self)]
            nmspc.update(__hash__=__hash__)
        elif '__hash__' in nmspc:
            raise TypeError(
                'This type does not allow overriding __hash__ function.')
        elif '__get__' in nmspc:
            __origin_get__ = nmspc['__get__']
            argspec = inspect.getargspec(__origin_get__).args
            is_extended = len(argspec) == 4 and argspec[3] == 'key'
            @wraps(__origin_get__)
            def __get__(self, inst, type):
                if inst and not self.__key__:
                    self.__key__ = fumble_key_by_val(inst, self)
                return __origin_get__(self, inst, type, self.__key__
                ) if is_extended else __origin_get__(self, inst, type)
            nmspc.update(__get__=__get__)
        return super(incrementalHashType, mcl).__new__(mcl, name, bases, nmspc)
    def __call__(cls, *args, **kwargs):
        __key__ = kwargs.pop('__key__', None)
        increased = incrementalHashType.counter + 1
        self = cls.__new__(cls, *args, **kwargs)
        if __key__:
            self.__key__ = __key__
        incrementalHashType.hashdict[object.__hash__(self)] = increased
        self.__init__(*args, **kwargs)
        incrementalHashType.counter = increased
        return self

from ..descriptor.set import DescriptorSet

class IncrementalHashBase(object):
    __key = None
    def __get_key__(self):
        return self.__key
    def __set_key__(self, val):
        newkey = self.__key_set__(val)
        if not newkey:
            raise ValueError(
                '__key_set__ must return either a key or `NotImplemented`.')
        elif newkey is NotImplemented:
            return
        self.__key = newkey
    def __key_set__(self, key):
        return key
    __key__ = property(__get_key__, __set_key__)
    @classmethod
    def descriptor_set(cls, attrs=None):
        return DescriptorSet(cls, attrs)

IncrementalHash = incrementalHashType('IncrementalHashBase',
    (IncrementalHashBase,), dict(__doc__= """
class Descriptor(IncrementalHash):
    def __get__(self, inst, type): # as-is
    def __get__(self, inst, type, key): # benefits key automatically provided as
                                        # in `__key__` attribute
When `__key__` is set, `__key_set__` method is invoked.
>>> hash(Descriptor())
>>> 1
>>> hash(Descriptor())
>>> 2
>>> ...
class Something(object):
    field1 = Descriptor() # `__key__` will be automatically found at first access
    field2 = Descriptor(__key__='my_field') # `__key__` will be manually set
"""))
