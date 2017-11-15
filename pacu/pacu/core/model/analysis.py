from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy.types import PickleType

from . import Base
from . import MutableDict

class AnalysisV1(Base):
    __tablename__ = 'analysis_v1'
    id = Column(Integer, primary_key=True)
    createdat = Column(DateTime, default=datetime.utcnow)
    type = Column(Unicode(256)) # for i3d
    title = Column(Unicode(256))
    user = Column(Unicode(256)) # relationship with users
    desc = Column(Unicode(256))
    imagesrc = Column(Unicode(512)) # path
    conditionid = Column(Integer) # path
    data = Column(MutableDict.as_mutable(PickleType), default=dict)

    # host = Column(Unicode(512)) # path
    # index = Column(Integer) # path
    # relationsship with recordings/experiment
    # relationsship with ? rois?
    # relationsship with ? objects?
