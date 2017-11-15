from sqlalchemy import (Column, Integer, Unicode,
                        Boolean, Date, Float, PickleType)

from pacu.core.model import Base
from pacu.core.model import PKColumn
from pacu.core.model.newtype import ListIntText
from pacu.core.model.newtype import ListFloatText

class VisStim2P(Base):
    __tablename__        = '2P_visual_stims'
    id                   = PKColumn(Integer)
    mouse_id             = Column(Integer)
    experimenter_id      = Column(Integer)
    date                 = Column(Date)
    filename             = Column(Unicode(255))
    stimulus_type        = Column(Unicode(255))
    orientations         = Column(ListFloatText)
    spatial_frequencies  = Column(ListFloatText)
    temporal_frequencies = Column(Unicode(255))
    nReps                = Column(Integer)
    nConditions          = Column(Integer)
    blankOn              = Column(Boolean)
    flickerOn            = Column(Boolean)
    sequence             = Column(ListIntText)
    duration_S           = Column(Float)
    duration_F           = Column(Float)
    waitinterval_S       = Column(Float)
    waitinterval_F       = Column(Float)
    condition_S          = Column(Float)
    condition_F          = Column(Float)
    ontimes_S            = Column(ListFloatText)
    ontimes_F            = Column(ListFloatText)
    total_time_S         = Column(Float)
    captureFrequency     = Column(Float)

# from pacu.profile import manager
# from pacu.core.method.twophoton.frequency.spatial.meta import SpatialFrequencyMeta
# ed = manager.get('db').section('ed')()
# qwe = ed.query(VisStim2P).order_by(VisStim2P.id.desc()).get(1236)
# a = SpatialFrequencyMeta(qwe)
# print qwe.serialize()
