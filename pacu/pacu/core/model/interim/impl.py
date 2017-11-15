from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy.types import PickleType

from .. import Base
from pacu.profile import manager
from pacu.ext.sqlalchemy.orm import session
from pacu.core.service.analysis.mapper.scanbox.data import ScanboxData

entry = dict(
    scanbox_data = ScanboxData
)

class Interim(Base):
    __tablename__ = 'interim'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    name = Column(Unicode(256))
    type = Column(Unicode(256))
    data = Column(PickleType)
    @classmethod
    def refresh(cls, type):
        try:
            data_set = entry.get(type).populate()
            s = session.get_scoped(engine)
            purge_count = s.query(cls).filter_by(type=type).delete()
            print 'INTERIM: purged {} item(s) for {}.'.format(purge_count, type)
            items = [cls(type=type, name=name, data=data)
                for name, data in data_set]
            s.add_all(items)
            s.commit()
        except Exception as e:
            print 'INTERIM: model failed to refresh {} type'.format(type)
            print e
        else:
            print 'INTERIM: added {} item(s) for {}.'.format(len(items), type)

print 'INTERIM: module initialize...'
engine = manager.get('db').section('interim')()
Interim.__table__.create(engine, checkfirst=True)
Interim.refresh('scanbox_data')
# s = session.get_scoped(engine)
