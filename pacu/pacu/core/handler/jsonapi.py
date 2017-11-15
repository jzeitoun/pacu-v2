import sys
import importlib
import traceback

import ujson

from sqlalchemy.orm import load_only
from pacu.core.io.scanbox.model import db
from pacu.ext.tornado.web import RequestHandler

def print_exc():
    info = sys.exc_info()
    source = traceback.format_exception(*info)
    print '\n======== exception on api handling ========'
    traceback.print_exception(*info)
    print '======== exception on api handling ========\n'

class ResourceLocator(object):
    """
    'PACU_JSONAPI_MODULE_NAME' = 'pacu.core.io.scanbox.impl'
    'PACU_JSONAPI_SESSION_ARGUMENTS' = 'jc6', 'jc6_1_120_006.io'
    'PACU_JSONAPI_BASE_NAME' = 'SQLite3Base'

    l = ResourceLocator(module_name='pacu.core.io.scanbox.model.db',
        base_name='SQLite3Base', session_args=['jc6', 'jc6_1_120_006.io'])
    """
    def __init__(self, module_name, base_name, session_args):
        self.module_name = module_name
        self.base_name = base_name
        self.session_args = session_args
    @classmethod
    def from_headers(cls, headers):
        mn = headers.get('PACU_JSONAPI_MODULE_NAME')
        bn = headers.get('PACU_JSONAPI_BASE_NAME')
        sa = headers.get('PACU_JSONAPI_SESSION_ARGUMENTS').split(',')
        return cls(mn, bn, sa)
    def __repr__(self):
        return ('{name}('
            'module_name={s.module_name!r}, '
            'base_name={s.base_name!r}, '
            'session_args={s.session_args!r})'
        ).format(name=type(self).__name__, s=self)
    @property
    def module(self):
        return importlib.import_module(self.module_name)
    @property
    def Base(self):
        return getattr(self.module, self.base_name)
    @property
    def orms(self):
        return {cls.__tablename__: cls for cls in self.Base.__subclasses__()}
    @property
    def Session(self):
        return self.module.Session(*self.session_args)

from sqlalchemy import event

# Servers MUST send all JSON API data in response documents with
# the header Content-Type: application/vnd.api+json without
# any media type parameters.

# Servers MUST respond with a 415 Unsupported Media Type status code if
# a request specifies the header Content-Type: application/vnd.api+json with
# any media type parameters.

# Servers MUST respond with a 406 Not Acceptable status code if
# a request's Accept header contains the JSON API media type and
# all instances of that media type are modified with media type parameters.

from sqlalchemy import inspect

def find_record(session, include, ORM, id):
    entity = session.query(ORM).get(id)
    data = entity.resource_object
    included = []
    attributes = entity.attributes_object
    relationships = {}
    for rel in include:
        if not rel: continue
        rel_etts = getattr(entity, rel)
        rel_data = [ett.resource_object for ett in rel_etts]
        relationships[rel] = dict(data=rel_data)
        for ett in rel_etts:
            incl = ett.resource_object
            incl['attributes'] = ett.attributes_object
            included.append(incl)
    data['attributes'] = attributes
    data['relationships'] = relationships
    return dict(data=data, included=included)

# def find_all(session, include, ORM);
#     entity = session.query(ORM).get(id)
#     data = entity.resource_object
#     included = []
#     attributes = entity.attributes_object
#     relationships = {}
#     for rel in include:
#         if not rel: continue
#         rel_etts = getattr(entity, rel)
#         rel_data = [ett.resource_object for ett in rel_etts]
#         relationships[rel] = dict(data=rel_data)
#         for ett in rel_etts:
#             incl = ett.resource_object
#             incl['attributes'] = ett.attributes_object
#             included.append(incl)
#     data['attributes'] = attributes
#     data['relationships'] = relationships
#     return dict(data=data, included=included)

class JSONAPIHandler(RequestHandler):
    url = r'/jsonapi/(?P<tablename>[\w-]+)/?(?P<id>\d*)'
    def prepare(self):
        self.locator = ResourceLocator.from_headers(self.request.headers)
        self.session = self.locator.Session()
        self.session.bind.echo = True
        event.listen(self.session, 'before_flush', db.before_flush)
        event.listen(self.session, 'after_commit', db.after_commit)
    def on_finish(self):
        event.remove(self.session, 'before_flush', db.before_flush)
        event.remove(self.session, 'after_commit', db.after_commit)
    def get(self, tablename, id):
        include = self.get_argument('include', '').split(',')
        ORM = self.locator.orms.get(tablename)
        if id:
            ja = find_record(self.session, include, ORM, id)
        else:
            ja = find_all(self.session, include, ORM)
        self.finish(ujson.dumps(ja))
        # filter_by = {
        #     fkey[7:-1]: fval[0]
        #     for fkey, fval in self.request.arguments.items()
        #     if fkey.startswith('filter[')}
        # filter_by = {
        #     k: False if v == 'false' else True if v == 'true' else v
        #     for k, v in filter_by.items()}
        # query = self.session.query(self.locator.orms.get(tablename))
        # if filter_by:
        #     query = query.filter_by(**filter_by)
        # data = query.get(id) if id else [entity.as_jsonapi for entity in query]
        # dumped = ujson.dumps(dict(data=data))
        # self.finish(dumped)
    def post(self, tablename, id):
        payload = ujson.loads(self.request.body)
        attrs = payload['data'].get('attributes') or {}
        rels = payload['data'].get('relationships') or {}
        s = self.session
        with s.begin():
            entity = self.locator.orms.get(tablename)(**attrs)
            for key, val in rels.items():
                if not val['data']:
                    continue
                orm = self.locator.orms.get(val['data']['type'])
                rel = s.query(orm).options(load_only('id')).get(val['data']['id'])
                setattr(entity, key, rel)
            s.add(entity)
        dumped = ujson.dumps(dict(data=entity.as_jsonapi))
        self.finish(dumped)
    def patch(self, tablename, id):
        payload = ujson.loads(self.request.body)
        attrs = payload['data'].get('attributes') or {}
        rels = payload['data'].get('relationships') or {}
        if not attrs and not rels:
            return self.set_status(204) # No Content
        s = self.session
        with s.begin():
            entity = s.query(self.locator.orms.get(tablename)).get(id)
            for key, val in attrs.items():
                setattr(entity, key, val)
            for key, val in rels.items():
                orm = self.locator.orms.get(val['data']['type'])
                rel = s.query(orm).options(load_only('id')).get(val['data']['id'])
                setattr(entity, key, rel)
        # with s.begin():
        #     entity = s.query(self.locator.orms.get(tablename)).get(id)
        #     for key, val in attrs.items():
        #         setattr(entity, key, val)
        ja = entity.as_jsonapi
        # import ipdb;ipdb.set_trace()
        # nd = dict(ja['relationships']['traces']['data'][0],attributes=dict(array=[]))
        # dumped = ujson.dumps(dict(data=ja, included=[nd]))
        dumped = ujson.dumps(dict(data=ja))

        self.finish(dumped)
    def delete(self, tablename, id):
        s = self.session
        with s.begin():
            entity = s.query(self.locator.orms.get(tablename)).get(id)
            # checkif we can use loadonly for relationship excluding
            s.delete(entity)
        self.finish(dict(meta={}))
        # dumped = ujson.dumps(dict(data=entity.as_jsonapi))
        # self.finish(dumped)
        # query.filter_by(id = id).update(**payload)
        # payload = {
        #     u'data': {
        #         u'relationships': {
        #             u'post': {
        #                 u'data': {
        #                     u'type': u'workspaces', u'id': u'1'
        #                 }
        #             }
        #         },
        #         u'attributes': {
        #             u'active': False,
        #             u'created_at': 1462516005,
        #             u'centroid': {},
        #             u'polygon': [
        #                 {u'y': 216, u'x': 332},
        #                 {u'y': 216, u'x': 443},
        #                 {u'y': 326, u'x': 433},
        #                 {u'y': 326, u'x': 332}
        #             ]
        #         },
        #         u'type': u'rois',
        #         u'id': u'2'
        #     }
        # }
        # payload = {
        #     u'data': {
        #         u'relationships': {
        #             u'post': {
        #                 u'data': {
        #                     u'type': u'workspaces', u'id': u'1'}
        #                 }
        #             },
        #         u'attributes': {
        #             u'polygon': [
        #                 {u'y': 241, u'x': 319},
        #                 {u'y': 241, u'x': 430},
        #                 {u'y': 351, u'x': 420},
        #                 {u'y': 351, u'x': 319}
        #             ]
        #         },
        #         u'type': u'rois',
        #         u'id': u'2'
        #     }
        # }

#     def prepare(self):
#         try:
#             api = self.path_kwargs['api']
#             args = self.path_kwargs['args']
#             try:
#                 self.http = importlib.import_module('pacu.api.%s.http' % api)
#             except ImportError as e:
#                 print 'ImportError:', e
#                 self.send_error(404)
#             else:
#                 self.args = filter(None, args.split('/'))
#                 self.kwargs = {key: val
#                     for key, vals in self.request.arguments.items()
#                     for val in vals}
#         except KeyError:
#             self.send_error(400)
#         except Exception as e:
#             print e
#             self.send_error(500)
#     # TODO: method extraction
#     def head(self, api, args):
#         try:
#             result = self.http.head(self.request, *self.args, **self.kwargs)
#         except TypeError as e:
#             print_exc()
#             self.set_status(400) # possible argument error
#             self.write(str(e))
#         except Exception as e:
#             print_exc()
#             self.set_status(403)
#             self.write(str(e))
#         else:
#             for key, val in result:
#                 self.add_header(key, val)
#             # self.finish(result)
#     def get(self, api, args):
#         if api == 'ping':
#             return self.http.get(self, *self.args, **self.kwargs)
#         try:
#             result = self.http.get(self.request, *self.args, **self.kwargs)
#         except TypeError as e:
#             print_exc()
#             self.set_status(400) # possible argument error
#             self.write(str(e))
#         except Exception as e:
#             print_exc()
#             self.set_status(403)
#             self.write(str(e))
#         else:
#             self.finish(result)
#     def post(self, api, args):
#         try:
#             result = self.http.post(self.request, *self.args, **self.kwargs)
#         except TypeError as e:
#             print_exc()
#             self.set_status(400) # possible argument error
#             self.write(str(e))
#         except Exception as e:
#             print_exc()
#             self.set_status(403)
#             self.write(str(e))
#         else:
#             self.finish(result)
#     def delete(self, api, args):
#         try:
#             result = self.http.delete(self.request, *self.args, **self.kwargs)
#         except TypeError as e:
#             print_exc()
#             self.set_status(400) # possible argument error
#             self.write(str(e))
#         except Exception as e:
#             print_exc()
#             self.set_status(403)
#             self.write(str(e))
#         else:
#             self.finish(result)

# Server Responsibilities

# Servers MUST send all JSON API data in response documents with
# the header Content-Type: application/vnd.api+json without
# any media type parameters.

# Servers MUST respond with a 415 Unsupported Media Type status code if
# a request specifies the header Content-Type: application/vnd.api+json with
# any media type parameters.

# Servers MUST respond with a 406 Not Acceptable status code if
# a request's Accept header contains the JSON API media type and
# all instances of that media type are modified with media type parameters.
