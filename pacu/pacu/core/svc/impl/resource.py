class Resource(object):
    def __init__(self, component, **kwargs):
        self.component = component
        for key, val in kwargs.items():
            setattr(self, key, val)
    @classmethod
    def bind(cls, *deps):
        def __call__(self, *args):
            if len(deps) != len(args):
                raise TypeError('Does not match between a number of '
                    'dependencies({}) and arguments({}).'.format(deps, args))
            self.current = cls(self, **dict(zip(deps, args)))
            return self.current
        return __call__
    def __exit__(self, type, value, tb):
        pass
