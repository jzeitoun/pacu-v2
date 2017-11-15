from .. import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import DateTime

class Mice(Base):
    __tablename__ = 'mice'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    sex = Column(Unicode(255))
    DOB = Column(DateTime)
    DOD = Column(DateTime)
