from sqlalchemy import inspect
from sqlalchemy.schema import CreateColumn
from sqlalchemy import schema

from pacu.util import identity
from pacu.util.path import Path
from pacu.profile import manager
from pacu.core.io.scanbox.model import relationship as sbxrels
from pacu.core.io.scanbox.model.relationship import *
from pacu.core.io.scanbox.model.base import SQLite3Base

opt = manager.instance('opt')
userenv = identity.path.userenv


# glab = manager.get('db').section('glab')
# bind = glab()().bind

def fix_incremental(meta, bind):
    """
    meta = schema.SQLite3Base.metadata
    bind = io.db_session.bind
    schema.fix_incremental(meta, bind)
    """
    meta.create_all(bind=bind, checkfirst=True)
    ref = inspect(bind)
    for table in meta.sorted_tables:
        orm_cols = set(col.name for col in table.c)
        ref_cols = set(col['name'] for col in ref.get_columns(table.name))
        col_to_create = orm_cols - ref_cols
        col_to_delete = ref_cols - orm_cols
        if col_to_create:
            print table.name, 'has diff to create', col_to_create
            with bind.begin() as conn:
                for col_name in col_to_create:
                    col = table.c.get(col_name)
                    column_sql = CreateColumn(col).compile(bind).string
                    sql = 'ALTER TABLE {} ADD COLUMN {}'.format(table.name, column_sql)
                    if col.default:
                        sql += ' DEFAULT {!r}'.format(col.default.arg) # can break when a pickle type has callable default.
                    if not col.nullable:
                        sql += ' NOT NULL'
                    print 'executing sql: ' + sql
                    conn.execute(sql)

            # Workaround to ensure updated DBs start with "False" in ignore column
            if list(col_to_create)[0] == 'ignore':
                sessionmaker = get_sessionmaker(bind.url.database)
                session = sessionmaker()
                query_object = {'dttrialdff0s': DTTrialDff0, 'trials': Trial}[table.name]
                items = session.query(query_object).all()
                for item in items:
                    item.ignore = False
                session.flush()

        if col_to_delete:
            print table.name, 'has diff to delete', col_to_delete, 'maybe later version.'
            """
            BEGIN TRANSACTION;
            CREATE TEMPORARY TABLE t1_backup(a,b);
            INSERT INTO t1_backup SELECT a,b FROM t1;
            DROP TABLE t1;
            CREATE TABLE t1(a,b);
            INSERT INTO t1 SELECT a,b FROM t1_backup;
            DROP TABLE t1_backup;
            COMMIT;
            """

def upgrade(metadata, bind):
    metadata.create_all(bind)
    fix_incremental(metadata, bind)

def recreate(dbpath='', echo=True):
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://{}'.format(
        '/' + str(dbpath) if dbpath else ''
    ), echo=echo)
    SQLite3Base.metadata.drop_all(engine)
    SQLite3Base.metadata.create_all(engine)
    return engine

def get_sessionmaker(dbpath, echo=True, autocommit=True, **kw):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    path = Path(dbpath)
    engine = create_engine('sqlite:///{}'.format(dbpath),
        echo=echo, **kw) if path.is_file() else recreate('', echo=echo)
    return sessionmaker(engine, autocommit=autocommit)

def Session(ioname, echo=True):
    """
    ioname = "jc6/jc6_1_120_006.io"
    sm = sessionmaker(ioname)
    Session = sm()
    session = Session()
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    dbpath = userenv.joinpath('scanbox', ioname, 'db.sqlite3')
    engine = create_engine('sqlite:///{}'.format(dbpath),
        echo=echo, convert_unicode=True)
    return sessionmaker(engine, autocommit=False)

def engine(ioname, echo=True):
    from sqlalchemy import create_engine
    dbpath = userenv.joinpath('scanbox', ioname, 'db.sqlite3')
    return create_engine('sqlite:///{}'.format(dbpath),
        echo=echo, convert_unicode=True)

def find_orm(tablename):
    return {c.__tablename__: c
            for c in SQLite3Base.__subclasses__()}.get(tablename)

def before_flush(session, flush_context, instances):
    for dirty in session.dirty:
        if hasattr(dirty, 'before_flush_dirty'):
            dirty.before_flush_dirty(session, flush_context)
    for new in session.new:
        if hasattr(new, 'before_flush_new'):
            new.before_flush_new(session, flush_context)
    for deleted in session.deleted:
        if hasattr(deleted, 'before_flush_deleted'):
            deleted.before_flush_deleted(session, flush_context)
def after_flush(session, flush_context):
    for new in session.new:
        if hasattr(new, 'after_flush_new'):
            new.after_flush_new(session, flush_context)
    # for dirty in session.dirty:
    #     keys = [attr.key for attr in inspect(dirty).attrs
    #         if attr.history.has_changes()]
    #     dirty.__flushed_attrs__ = tuple(keys)
    #     dirty.__committed_attrs__.extend(keys)
def after_begin(session, transaction, connection):
    # print 'AFTER BEGIN'
    for model in session.identity_map.values():
        model.__flushed_attrs__ = ()
        model.__committed_attrs__ = []
def after_commit(session):
    # print 'AFTER COMMIT'
    for model in session.identity_map.values():
        model.__flushed_attrs__ = ()
        model.__committed_attrs__ = tuple(model.__committed_attrs__)
def after_rollback(session):
    # print 'AFTER ROLLBACK'
    for model in session.identity_map.values():
        model.__flushed_attrs__ = ()
        model.__committed_attrs__ = []

SQLite3Base.__flushed_attrs__ = ()
SQLite3Base.__committed_attrs__ = ()

def list_orms():
    return [getattr(sbxrels, k) for k in sbxrels.__all__]
