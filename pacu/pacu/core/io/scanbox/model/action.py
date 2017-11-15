import cv2
import sys
import traceback
import numpy as np
from sqlalchemy import Column, Integer, UnicodeText
from sqlalchemy.types import PickleType

from pacu.core.io.scanbox.model.base import SQLite3Base

class Action(SQLite3Base):
    __tablename__ = 'actions'
    model_name = Column(UnicodeText)
    model_id = Column(Integer)
    query_only = Column(PickleType, default=['id'])
    action_name = Column(UnicodeText)
    action_args = Column(PickleType, default=[])
    action_kwargs = Column(PickleType, default={})
    status_code = Column(Integer, default=503)
    status_text = Column(UnicodeText, default=u'') # assign automatically
    # status_text = Column(UnicodeText, default=u'Service Unavailable')
    def before_flush_new(self, session, context): # before attached to session
        print 'An action running through!', self.__dict__
        Model = self._decl_class_registry.get(self.model_name)
        model = session.query(Model).get(self.model_id)
        try:
            result = getattr(model, self.action_name)(
                *self.action_args or [], **self.action_kwargs or {})
            self.status_code = 200
            if result is not None:
                self.meta = result
        except Exception as e:
            reason = '<br/>'.join(traceback.format_exception(*sys.exc_info()))
            self.status_code = 500
            self.status_text = reason
