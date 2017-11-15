from sqlalchemy.orm import deferred, relationship
from sqlalchemy import Column, Integer, Unicode, Date, PickleType, ForeignKey
from ext.model import Base, PKColumn

class AnalysisM2M(Base):
    __tablename__ = 'analysis2p_m2m'
    referer_id = PKColumn(ForeignKey('analysis2p.id'))
    compare_id = PKColumn(ForeignKey('analysis2p.id'))
m2m = AnalysisM2M.__table__

class Analysis(Base):
    __tablename__   = 'analysis2p'
    id              = PKColumn(Integer)
    mouse_id        = Column(Integer)
    experimenter_id = Column(Integer)
    date            = Column(Date)
    filename        = Column(Unicode(255))
    data            = Column(PickleType)
    references      = relationship('Analysis',
        primaryjoin   = id==m2m.c.compare_id,
        secondaryjoin = id==m2m.c.referer_id,
        secondary     = m2m,
        backref       = 'citations'
    )

