from collections import OrderedDict

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column

class Base(object):
    __table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}
    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()
    # id =  Column(Integer, primary_key=True)
    # created_at = Column(DateTime, default=datetime.utcnow)
    def extract(self):
        attributes = OrderedDict([
            (c.name, getattr(self, c.name))
            for c in self.__mapper__.c if c.name not in ['id']
        ])
        return dict(
            type = self.__tablename__,
            id = self.id,
            attributes = attributes
        )
    def serialize(self, type=None, normalizer=str):
        attributes = OrderedDict([
            (c.name, normalizer(getattr(self, c.name)))
            for c in self.__mapper__.c if c.name not in ['id']
        ])
        return dict(
            type = type or self.__tablename__,
            id = self.id,
            attributes = attributes
        )

Base = declarative_base(cls=Base)

def PKColumn(*args, **kwargs):
    return Column(*args, primary_key=True, **kwargs)

