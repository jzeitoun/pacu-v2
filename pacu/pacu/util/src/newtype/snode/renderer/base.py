import ujson

class BaseRenderer(list):
    def __new__(cls, iterable, context, extras):
        return super(BaseRenderer, cls).__new__(cls, iterable)
    def __init__(self, iterable, context, extras):
        super(BaseRenderer, self).__init__(iterable)
        self.context = context
        self.extras = extras
    def __iter__(self):
        for item in list.__iter__(self):
            mapping = item._vars(*self.extras)
            mapping.update(item.on_map(mapping) or {})
            yield mapping
    def to_json(self):
        return dict(data=self, actions=self.context['actions'])
