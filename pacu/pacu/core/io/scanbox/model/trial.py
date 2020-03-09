import cv2
import numpy as np
from sqlalchemy import Column, Integer, UnicodeText, Float, Boolean
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base

class Trial(SQLite3Base):
    __tablename__ = 'trials'
    on_time = Column(Float)
    off_time = Column(Float)
    ori = Column(Float)
    sf = Column(Float)
    tf = Column(Float)
    contrast = Column(Float)
    sequence = Column(Integer)
    order = Column(Integer)
    ran = Column(Integer)
    flicker = Column(Boolean, default=False)
    blank = Column(Boolean, default=False)
    ignore = Column(Boolean, default=False, nullable=True)
