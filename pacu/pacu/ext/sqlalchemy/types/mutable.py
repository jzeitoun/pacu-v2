from sqlalchemy.ext.mutable import Mutable

class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        else:
            return value
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()
    def __getstate__(self):
        return dict(self)
    def __setstate__(self, state):
        self.update(self)
    def __dir__(self):
        return list(self)
    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            return super(MutableDict, self).__getattr__(key)
    def __setattr__(self, key, val):
        if key in self:
            self[key] = val
        else:
            super(MutableDict, self).__setattr__(key, val)
