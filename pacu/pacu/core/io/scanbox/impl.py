from __future__ import division

import numpy as np

from pacu.util.path import Path
from pacu.profile import manager
from pacu.core.io.scanbox.view.sbx import ScanboxSBXView
from pacu.core.io.scanbox.view.mat import ScanboxMatView
from pacu.core.io.scanbox.view.ephys import ScanboxEphysView
from pacu.core.io.scanbox.channel import ScanboxChannel
from pacu.core.io.scanbox.model import db
from pacu.core.model.experiment import ExperimentV1

opt = manager.instance('opt')
glab = manager.get('db').section('glab')

class sessionBinder(type):
    @classmethod
    def bind(mcl, session, orm):
        return mcl('SessionBound{}'.format(orm.__name__),
            (object, ), dict(session=session, orm=orm))
    def __call__(cls, *args, **kwargs):
        return cls.orm(*args, **kwargs)
    @property
    def queried(cls):
        return cls.session.query(cls.orm)
    def get(cls, id):
        return cls.queried.get(id)
    def all(cls):
        return cls.queried.all()
    def one(cls, **kwargs):
        return cls.queried.filter_by(**kwargs).one()
    def one_or_none(cls, **kwargs):
        return cls.queried.filter_by(**kwargs).one_or_none()
    def first(cls):
        return cls.queried.first()
    # direct SQL command
    def create(cls, payload):
        with cls.session.begin():
            inst = cls(**payload)
            cls.session.add(inst)
            return inst
    def delete(cls, payload):
        return cls.queried.filter_by(**payload).delete()
    def upsert(cls, payload):
        # with cls.session.begin() as t:
        #     roi = t.session.merge(cls(**payload))
        #     t.session.flush()
        #     return {key: getattr(roi, key) for key in payload.keys()}
        with cls.session.begin():
            roi = cls.session.merge(cls(**payload))
            cls.session.flush()
            return {key: getattr(roi, key) for key in payload.keys()}
    read = NotImplemented
    def __dir__(self):
        return ['queried', 'get', 'all', 'one',
            'one_or_none', 'first', 'create',
            'read', 'upsert', 'delete']

class SessionBoundNamespace(object):
    """
    session = SessionBoundNamespace(session, db.Session, db.ROI)
    """
    def __init__(self, session, *orms):
        self._session = session
        self.__dict__.update({
            orm.__name__: sessionBinder.bind(session, orm)
            for orm in orms})
    def __enter__(self):
        return self._session, self._session.begin()
    def __exit__(self, *args):
        print 'SESSION BOUND NAMESPACE __EXIT__'
        print args

from sqlalchemy import event

class ScanboxIO(object):
    session = None
    channel = None
    def __init__(self, path):
        self.path = Path(path).ensure_suffix('.io')
        self.session = SessionBoundNamespace(
            self.db_session_factory(),
            db.Workspace, db.ROI, db.Datatag, db.Condition, db.Trial)
    @property
    def is_there(self):
        return self.path.exists()
    @property
    def db_path(self):
        return self.path.joinpath('db.sqlite3').absolute()
    @property
    def db_session_factory(self):
        maker = db.get_sessionmaker(self.db_path)
        # sessionmaker can configure without bind(engine)
        # so setup event first. it's doable.
        # event.remove(maker, 'before_attach', db.SQLite3Base.before_attach)
        event.listen(maker, 'before_flush', db.before_flush)
        event.listen(maker, 'after_commit', db.after_commit)

        return maker
    def set_workspace(self, id):
        self.workspace_id = id
        return self
    @property
    def workspace(self):
        return self.session.Workspace.one_or_none(id=self.workspace_id)
    @property
    def mat(self):
        return ScanboxMatView(self.path.with_suffix('.mat'))
    @property
    def sbx(self):
        return ScanboxSBXView(self.path.with_suffix('.sbx'))
    @property
    def ephys(self):
        return ScanboxEphysView(self, self.path.with_suffix('.txt'))
    @property
    def attributes(self):
        error = None
        try:
            workspaces = self.session.Workspace.all()
        except Exception as e:
            notable = 'no such table' in str(e)
            nocolumn = 'no such column' in str(e)
            workspaces = []
            error = dict(notable=notable, nocolumn=nocolumn,
                    detail=str(e), type=type(e).__name__)
        return dict(
            hops = self.path.relative_to(opt.scanbox_root).parts,
            path = self.path.str,
            is_there = self.is_there,
            mat = self.mat,
            sbx = self.sbx,
            error = error,
            mode = 'uni' if self.mat.scanmode else 'bi',
            workspaces = workspaces)
    def get_channel(self, number):
        return ScanboxChannel(self.path.joinpath('{}.chan'.format(number)))
    def set_channel(self, number):
        self.channel = self.get_channel(number)
        return self
    def remove_io(self):
        self.path.rmtree()
        self.session = SessionBoundNamespace( # unnecessary implementation
            self.db_session_factory(),
            db.Workspace, db.ROI, db.Datatag, db.Condition, db.Trial)
        return self.attributes
    def import_raw(self):
        self.path.mkdir_if_none()
        db.recreate(self.db_path)
        self.session = SessionBoundNamespace(
            self.db_session_factory(),
            db.Workspace, db.ROI, db.Datatag, db.Condition, db.Trial)
        self.import_exp_as_condition()
        for chan in range(self.mat.nchannels):
            self.get_channel(chan).import_with_io(self)
        return self.attributes
    def import_exp_as_condition(self):
        s = glab()
        entity = s.query(ExperimentV1).filter_by(keyword=self.path.stem).one_or_none()
        if entity:
            print 'There is matching condition data in ED for {!r}'.format(
                self.path.stem)
            try:
                session = self.session._session
                with session.begin():
                    condition = db.Condition.from_expv1(entity)
                    condition.trials.extend([db.Trial.init_and_update(**trial) for trial in entity])
                    session.add(condition)
            except Exception as e:
                print 'Condition import failed with reason below,', str(e)
        else:
            print 'There is no matching condition data in ED for {!r}'.format(
                self.path.stem)
    def upgrade_db_schema(self):
        db.upgrade(db.SQLite3Base.metadata,
            self.db_session_factory.kw.get('bind'))
        return self.attributes

def ScanboxIOFetcher(mouse, day, io_name, workspace_id):
    root = manager.instance('opt').scanbox_root
    path = Path(root).joinpath(mouse, day, io_name)
    return ScanboxIO(path).set_workspace(workspace_id).set_channel(0)
