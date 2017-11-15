import ujson

from datetime import timedelta
from datetime import datetime
from pacu.util.path import Path
from pacu.profile import manager
from pacu.util import identity
from pacu.core.model.experiment import ExperimentV1 as EXPV1
from pacu.core.io.scanbox.model import db as schema
from pacu.core.io.scanbox.impl2 import ScanboxIO
from pacu.api.json.http.scanbox_manager import Location
from pacu.api.json.http.scanbox_manager import DataStoreLocator

opt = manager.instance('opt')
xulab = manager.get('db').section('xulab')

try:
    datastore = Location(opt.miniscope_root)
    workspace = Location(identity.path.userenv.joinpath('miniscope'))
    datastore.path.mkdir_if_none()
    workspace.path.mkdir_if_none()
except Exception as e:
    print e

class MiniscopeDataStoreLocator(DataStoreLocator):
    @property
    def rendered(self):
        items, dirs = [], []
        for item in self.items_within:
            if not item.is_dir():
                continue
            if all(map(item.has_file, ['behavCam1.avi', 'msCam1.avi', 'timestamp.dat'])):
                items.append(self.render_item(item))
            else:
                dirs.append(self.render_dir(item))
        return dict(items=items, dirs=dirs)
    def render_dir(self, item):
        return dict(name=item.name, ctime=item.stat().st_ctime)
    def render_item(self, item):
        return dict(name=item.stem, ctime=item.stat().st_ctime,
                path=item.str, size=item.size.str)

def get_path(req):
    return dict(
        datastore=datastore.json,
        workspace=workspace.json,
        datastore_nav='/api/json/miniscope_manager/nav_ds',
        workspace_nav='/api/json/miniscope_manager/nav_ws',
    )

def get_nav_ds(req, hops, glob, days):
    path = datastore.path.joinpath(*hops.split(','))
    locator = MiniscopeDataStoreLocator(path, glob, timedelta(int(days)))
    return locator.rendered

def get_conditions(req):
    try:
        query = xulab().query(
            EXPV1.id, EXPV1.created_at, EXPV1.keyword, EXPV1.duration
        ).order_by(EXPV1.created_at.desc())
        return [entity._asdict() for entity in query]
    except Exception as e:
        print 'Database not working', e
        return []

def get_ios(req):
    dataset = []
    for path in workspace.path.rglob('**/*.io'):
        try:
            data = ScanboxIO(path.relative_to(workspace.path)).toDict()
        except Exception as e:
            print path, e
        else:
            dataset.append(data)
    return dataset

# def fix_all():
#     for path in workspace.path.rglob('**/*.io'):
#         print 'fix', path
#         ScanboxIO(path.relative_to(workspace.path)).fix_db_schema()
# 
# def get_workspace_id(req, iopath=None, wsname=None):
#     io = ScanboxIO(iopath)
#     ws = io.condition.object_session.query(
#         schema.Workspace.id).filter_by(name=unicode(wsname)).one()
#     return ws.id
# def get_rois_exported(req, io, ws):
#     io = ScanboxIO(io)
#     ws = io.condition.workspaces.filter_by(name=ws).first
#     data = dict(rois = [r.export() for r in ws.rois])
#     return data
#     # req.handler.set_header('Content-Type', 'application/octet-stream')
#     # req.handler.set_header('Content-Disposition', 'attachment; filename=oarubgarg.json')
#     # req.handler.write(ujson.dumps(data))
# 
# def delete_io(req, iopath):
#     io = ScanboxIO(iopath)
#     io.path.resolve()
#     io.remove_io()
# 
# def post_workspace(req, iopath, name):
#     io = ScanboxIO(iopath)
#     io.path.resolve()
#     io.condition.append_workspace(name)
#     return dict(name=name)
# 
# def delete_workspace(req, iopath, name):
#     io = ScanboxIO(iopath)
#     io.path.resolve()
#     session = io.db_session
#     with session.begin():
#         ws = session.query(schema.Workspace).filter_by(name=name).one()
#         session.delete(ws)
# 
# def patch_db(req, iopath):
#     # how can i find exp id...
#     raise NotImplementedError
# #     io = ScanboxIO(iopath)
# #     io.path.resolve()
# #     import ipdb;ipdb.set_trace()
# #     session = io.db_session
# #     with session.begin():
# #         ws = session.query(schema.Workspace).filter_by(name=name).one()
# #         session.delete(ws)
