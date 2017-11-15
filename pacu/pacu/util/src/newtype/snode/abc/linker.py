from collections import defaultdict

from ..abc.mapper import Mappable

class Linkable(Mappable):
    InfoNode = None
    context = None
    def __init__(self, data=None, anchor=None, **kwargs): #, action=None, **kwargs):
        self.data = data
        self.anchor = anchor
        self.context = defaultdict(list) if anchor is None else anchor.context
        if not anchor:
            self.context['actions'] = []
        self.__dict__.update(kwargs)
    def link(self, Node, data=None, **kwargs):
        return Node(data=data, anchor=self, **kwargs)
    def link_info_node(self, data=None, **kwargs):
        return (self.InfoNode or Linkable)(
            data=data, anchor=self, **kwargs)
    def on_yield(self):
        self.context[self.__class__.__name__].append(self)
        return self

class Actable(object):
    def action(self, event):
        fname = 'on_{}'.format(event)
        for node in self.routable(self.data):
            func = getattr(node, fname, None)
            if func:
                return func()
        else:
            raise TypeError(
                'Graph `{}` does not support action `{}` with data `{}`'.format(
                self.__class__.__name__, event, self.data))
