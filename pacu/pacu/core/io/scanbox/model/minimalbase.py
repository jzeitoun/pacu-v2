from sqlalchemy import create_engine, Column, Integer, UnicodeText, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import PickleType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

MinimalBase = declarative_base()

class Workspace(MinimalBase):
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True)
    name = Column(UnicodeText, unique=True)
class ROI(MinimalBase):
    __tablename__ = 'rois'
    id = Column(Integer, primary_key=True)
    polygon = Column(PickleType, default=[])
    # neuropil 

ROI.workspace_id = Column(Integer, ForeignKey(Workspace.id))
Workspace.rois = relationship(ROI, order_by=ROI.id)
