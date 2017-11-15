from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import DateTime

from . import Base

class AppConfiguration(Base):
    """
    For the application setting
    """
    __tablename__ = 'app_configuration'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(Unicode(256))
