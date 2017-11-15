from weakref import WeakKeyDictionary

class XMLProperty(object):
    def __init__(self, tagname):
        self.tagname = tagname
        self.registry = WeakKeyDictionary()
    def __get__(self, inst, cls):
        return (self if not inst else
                self.registry.get(inst))
    def __set__(self, inst, value):
        self.registry[inst] = value

class XMLProxy(object):
    def __init__(self, prop, attr):
        self.prop = prop
        self.attr = attr
    def __repr__(self):
        return repr(self.attr)
    @property
    def element(self):
        return '<{0}>{1}</{0}>'.format(self.prop.tagname, self.attr)
    @property
    def iterable(self):
        return '<{0}>{1}</{0}>'.format(self.prop.tagname, map(format, self.attr))
