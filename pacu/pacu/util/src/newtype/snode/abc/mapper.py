from collections import OrderedDict

from ....compat.iterable import tuple

class BaseMapper(object):
    defaults = {}
    def __init__(self, node):
        self.node = node
    def vars(self, data, anchor, context):
        return OrderedDict(self.defaults)
    @classmethod
    def extend(cls, **kwargs):
        defaults = dict(kwargs, **cls.defaults)
        return type('Dynamic{}'.format(cls.__name__), (cls,), dict(defaults=defaults))

class IdentityMapper(BaseMapper):
    def vars(self, data, anchor, context):
        vars = super(IdentityMapper, self).vars(data, anchor, context)
        more = OrderedDict(
            modname = self.node.__module__,
            clsname = self.node.__class__.__name__,
            data = str(data)
        )
        vars.update(more)
        return vars

class Mappable(object):
    mappers = ()
    def _vars(self, *extras):
        data, anchor, context = self.data, self.anchor, self.context
        base = IdentityMapper(self).vars(data, anchor, context)
        for m in [M(self) for M in tuple.like(self.mappers) + extras]:
            base.update(m.vars(data, anchor, context) or [])
        return base
    def on_map(self, mapping):
        pass

# z = OrderedDict(a=1,b=2,c=3)
# x = OrderedDict(one=11, two=22, three=33)
# c = OrderedDict(first='first', second='second')
