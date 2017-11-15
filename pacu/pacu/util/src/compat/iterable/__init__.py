import ujson

class tuple(tuple):
    @classmethod
    def like(cls, obj):
        try:
            return cls(obj.split())
        except AttributeError as e:
            try:
                return cls(obj)
            except TypeError as e:
                return () if obj is None else (obj,)
class dict(dict):
    @property
    def json(self):
        return ujson.dumps(self)
class list(list):
    @property
    def json(self):
        return ujson.dumps(self)
