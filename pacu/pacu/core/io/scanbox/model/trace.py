from sqlalchemy import Column, Unicode
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base

class Trace(SQLite3Base):
    __tablename__ = 'traces'
    array = Column(PickleType, default=[])
    color = Column(Unicode(24))
    category = Column(Unicode(64))
    def invalidate(self):
        self.array = []
    def refresh(self):
        self.array = self.roi.compute(self.category)
