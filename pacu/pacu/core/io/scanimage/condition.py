class ScanimageCondition(object):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
    def extract(self):
        attributes = {
            key: getattr(self, key) for key in 'spatial_frequencies'.split()
        }
        return dict(attributes=attributes)
