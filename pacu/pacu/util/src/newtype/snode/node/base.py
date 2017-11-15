from operator import attrgetter
from itertools import chain

from ..abc.linker import Linkable
from ..abc.linker import Actable
from ..renderer.base import BaseRenderer

class BaseNode(Actable, Linkable):
    routes = ()
    sort_keys = ()
    checker = None
    nodes = None
    Renderer = BaseRenderer
    def check(self, that):
        return False
    def unfold(self):
        yield self.data
    def filter(self, props):
        return props
    def induce(self):
        return ()
    def makeup(self, nodes):
        return ()
    def routable(self, data):
        for node in [N(data, self) for N in self.routes]:
            if (node.checker or node.check)(data):
                yield node
    def gather(self, nodes):
        for data in self.filter(self.unfold()):
            for node in self.routable(data):
                if node.routes:
                    for subnode in node:
                        yield subnode
                    continue # or stay and deal with itself
                selfnodes = node.nodes() if callable(node.nodes)            \
                       else node.nodes   if hasattr(node.nodes, '__iter__') \
                       else (node,)    # determination of actual yielding point
                for node in selfnodes: # i.e. no routes, no nodes
                    yield node.on_yield()
    def sorted(self, inodes, gnodes, mnodes):
        return chain(inodes,
            (sorted(gnodes, key=attrgetter(*self.sort_keys))
                if self.sort_keys else gnodes), mnodes)
    def __iter__(self):
        self.context.clear()
        inodes = list(self.induce() or [])
        gnodes = list(self.gather(inodes) or [])
        mnodes = list(self.makeup(gnodes) or [])
        return self.sorted(inodes, gnodes, mnodes)
    iter = __iter__
    def render(self, *extras):
        return self.Renderer(list(self), self.context, extras)
