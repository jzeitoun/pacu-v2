from collections import OrderedDict

from ..inspect.get import clsname
from .memoized import MemoizedProperty

class DescriptorMemoizedProperty(MemoizedProperty):
    pass
class DescriptorView(object):
    """
    DescriptorView is a handy way to provide an attribute gateway among
    same descriptors.
    """
    def __new__(cls, ptype):
        """
        This weird implementation was necessary to defer
        the instantiation late as possible.
        This class needs to already exist in a class design as an instance.
        """
        # `__new__` of this class takes `ptype` so below line
        # passes ptype as well in order to avoid recursion.
        deferred = object.__new__(cls, ptype) # allocated!
        # `owner` below means like a `self` of an instance that has
        # an instance of `DescriptorView`
        def init(owner): # so this method actually belongs to those instances.
            # deferred is a `self` of `DescriptorView`.
            deferred.__init__(owner, ptype)
            return deferred
        # at this point deferred `init` has been wrapped 
        # so it will be called only once per owner instances.
        return property(init) # DescriptorMemoizedProperty(init) <- this hides other instances view.
        # so this time it goes with just a `property`

    def __init__(self, owner, ptype):
        # the view will catch all the instances of `ptype` type for `owner`
        self.__owner = owner
        self.__otype = type(owner)
        self.__ptype = ptype
        self.__props = []
        # iterate over class because we don't want
        for attr in dir(self.__otype): # to touch already fulfilled properties.
            # is this class-level attr is desired property type?
            clslevel_attr = getattr(self.__otype, attr)
            if isinstance(clslevel_attr, self.__ptype):
                if not isinstance(clslevel_attr, DescriptorMemoizedProperty):
                    self.__props.append(attr)
    def __getattr__(self, key):
        return getattr(self.__otype, key)
    def __dir__(self): # simply yields desired property instance
        return self.__props
    def __iter__(self):
        return iter(getattr(self, attr) for attr in dir(self))
    def __vars__(self): # not an official magic!
        return OrderedDict([
            (key, val.__get__(self.__owner, self.__otype))
            for key, val in zip(dir(self), list(self))
        ])
"""
class T(object):
    normal = 'value'
    another = 'value'
    @a_property
    def takesome(self):
        time.sleep(0.5)
        return 'it took some!'
    @a_property
    def eatalot(self):
        time.sleep(1)
        return 'it took a lot!'
    aps = DescriptorView(a_property)
t = T()
dir(t.mps)
list(t.mps)
"""
