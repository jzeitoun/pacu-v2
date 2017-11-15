from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.pool import StaticPool

from pacu.util.path import Path
from pacu.profile import manager
from pacu.core.model import Base

# import ipdb # will cause shell prompt change
# this can lead to broken tab-completion

def get_scoped(engine):
    from pacu.ext.sqlalchemy.orm import session
    return session.get_scoped(engine)

def default(profile):
    interpolated = profile.formatter.format(**vars(profile))
    engine = create_engine(interpolated, echo=profile.echo.bool)
    engine.__pacu_protect__ = profile.PROTECT.bool
    return get_scoped(engine)

def _create_sqlite_engine(uri, echo):
    return create_engine(uri, echo=echo,
        connect_args = dict(check_same_thread=False),
        poolclass = StaticPool)

def ephemeral(profile):
    from pacu.util import identity
    from pacu.core.model import fixture
    l = manager.instance('log')
    resource = identity.formattempfile('%s-db-engine-ephemeral.db')
    engine = _create_sqlite_engine(profile.uri + resource, profile.echo.bool)
    engine.__pacu_protect__ = profile.PROTECT.bool
    s = get_scoped(engine)
    if not Path(resource).is_file():
        fixture.base.setup(s)
        l.info('Tables of ephemeral db has initialized.')
    return s

def memory(profile):
    from pacu.core.model import fixture
    engine = _create_sqlite_engine(profile.uri, profile.echo.bool)
    engine.echo = False
    engine.__pacu_protect__ = profile.PROTECT.bool
    s = get_scoped(engine)
    fixture.base.setup(s)
    engine.echo = profile.echo.bool
    return s

def interim(profile):
    return memory(profile)

