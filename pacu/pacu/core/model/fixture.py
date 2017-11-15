from . import analysis_fixture  as analysis
from .auth import member_fixture as member

class base(object):
    @classmethod
    def make(cls, session):
        from . import Base
        Base.metadata.create_all(session.bind)
    @classmethod
    def drop(cls, session):
        if hasattr(session.bind, '__pacu_protect__'):
            if session.bind.__pacu_protect__:
                raise Exception('Can not drop a protected engine. '
                    'Please review your db.cfg settings with `PROTECT` item.')
        from . import Base
        Base.metadata.drop_all(session.bind)
    @classmethod
    def dump(cls, session):
        analysis.dump(session)
        member.dump(session)
    @classmethod
    def setup(cls, session=None):
        from . import Base
        if not session:
            from pacu.profile import manager
            from pacu.ext.sqlalchemy.orm.session import get_scoped
            session = get_scoped(manager.get('db').as_resolved())
        cls.drop(session)
        cls.make(session)
        cls.dump(session)
        return session
