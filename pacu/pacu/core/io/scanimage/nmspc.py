from collections import namedtuple

Item = namedtuple('Item', 'key val')

def pass_exception(func):
    def have_mercy(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            pass
    return have_mercy

AMBIGUOUS_ID = True, False, None

class HybridNamespace(dict):
    path = None
    defer_save = False
    @classmethod
    def from_path(cls, path):
        self = cls()
        self.path = path
        self.peak()
        return self
    def __repr__(self):
        return '{}({}, {})'.format(type(self).__name__,
            super(HybridNamespace, self).__repr__(), repr(vars(self)))
    def save(self):
        if self.defer_save:
            return
        self.path.dump_pickle(self)
        return self
    def load(self):
        return self.updated(self.path.load_pickle())
    @pass_exception
    def peak(self):
        return self.load()
    def clear(self):
        super(HybridNamespace, self).clear()
        self.save()
        return self
    @property
    def has_data(self):
        return self.path.is_file()
    def create(self):
        if self.has_data:
            raise Exception('Namespace `{}` already exists.'.format(self.path.stem))
        self.save()
    def unlink(self):
        if not self.has_data:
            raise Exception('Namespace `{}` does not exists.'.format(self.path.stem))
        self.path.unlink()
    def __delitem__(self, key):
        super(HybridNamespace, self).__delitem__(key)
        self.save()
    def __setitem__(self, key, val):
        super(HybridNamespace, self).__setitem__(key, val)
        self.save()
    def update(self, *args, **kwargs):
        super(HybridNamespace, self).update(*args, **kwargs)
        self.save()
    def updated(self, *args, **kwargs): # a notation for mutation
        self.update(*args, **kwargs)
        return self
    def setdefault(self, *args, **kwargs):
        rv = super(HybridNamespace, self).setdefault(*args, **kwargs)
        self.save()
        return rv
    def pop(self, key, default=None):
        rv = super(HybridNamespace, self).pop(key, default)
        self.save()
        return rv
    def remove(self, key):
        del self[key]
    def one(self):
        try:
            return Item(*next(iter(self.items())))
        except StopIteration:
            raise StopIteration('There is nothing yet.')
    def upsert(self, instance):
        try:
            id = instance.id
            if id in AMBIGUOUS_ID:
                raise ValueError(
                    '`id` `{}` is too ambiguous. '
                    'Please consider not using these ids `{}`.'.format(id, AMBIGUOUS_ID))
        except AttributeError as e:
            raise AttributeError('`upsert` requires the instance `{!r}` '
                'to have `id` attribute.'.format(instance))
        else:
            previous = super(HybridNamespace, self).setdefault(id, instance)
        vars(previous).update(vars(instance))
        self.save()
        return previous
    def upsert_bulk(self, *instances):
        with self.bulk_on:
            return [self.upsert(inst) for inst in instances]
    @property
    def bulk_on(self):
        self.defer_save = True
        return self
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.defer_save = False
        self.save()
