from sqlalchemy.orm import deferred, relationship
from sqlalchemy import Column, Integer, Unicode, Date, PickleType, ForeignKey
from ext.model import Base, PKColumn

class Stimulus(Base):
    __tablename__   = '2P_visual_stims'
    nReps               = Column(Integer)
    nConditions         = Column(Integer)
    sequence            = Column(Unicode(255))
    orientations        = Column(Unicode(255))
    spatial_frequencies = Column(Unicode(255))
    mouse_id            = PKColumn(Integer)
    date                = PKColumn(Date)
    filename            = PKColumn(Unicode(255))
