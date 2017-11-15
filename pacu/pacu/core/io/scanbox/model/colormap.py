from sqlalchemy import Column, Integer, Boolean, UnicodeText
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base

class Colormap(SQLite3Base):
    __tablename__ = 'colormaps'
    basename = Column(UnicodeText, default=u'jet')
    xmid1 = Column(Integer, default=25)
    ymid1 = Column(Integer, default=25)
    xmid2 = Column(Integer, default=75)
    ymid2 = Column(Integer, default=75)
