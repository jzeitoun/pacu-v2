from datetime import datetime
from collections import OrderedDict

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy import inspect, DateTime

def parallelize(iterable, func):
    for i in iterable:
        yield i, func(i)

class Base(object):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    def toDict(self):
        return self.as_jsonapi
    @property
    def as_jsonapi(self): # resource object
        resobj = dict(
            type = self.__tablename__,
            id = self.id,
            attributes = self.attributes,
            relationships = self.relationships)
        if hasattr(self, 'meta'):
            resobj['attributes']['meta'] = self.meta
        return resobj
    @property
    def attributes(self):
        return OrderedDict([
            (c.key, getattr(self, c.key))
        for c in inspect(type(self)).columns])
    @property
    def identity(self):
        return dict(id=self.id, type=self.__tablename__)
    @property
    def relationships(self):
        rels = inspect(type(self)).relationships
        return OrderedDict([
            (rel.key, dict(data=(
                    [o.identity for o in obj] if rel.uselist else obj.identity
                ))
            ) for rel, obj
              in parallelize(rels, lambda rel: getattr(self, rel.key)
            ) if obj
        ])
    @classmethod
    def init_and_update(cls, **kwargs):
        payload = {key: kwargs.pop(key)
            for key in cls.__mapper__.c.keys()
            if key in kwargs}
        self = cls(**payload)
        self.__dict__.update(kwargs)
        return self

    @property
    def resource_object(self):
        """
        type
        id
        -----------------
        attributes
        links
        meta
        relationships
        """
        return dict(id=self.id, type=self.__tablename__)
    @property
    def attributes_object(self):
        i = inspect(type(self))
        return OrderedDict([
            (c.key, getattr(self, c.key))
            for c in i.columns if c not in i.primary_key
        ])

SQLite3Base = declarative_base(cls=Base)
