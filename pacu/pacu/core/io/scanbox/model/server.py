import importlib

from flask import json
from flask import Flask
from flask import request
from flask_restless import APIManager
from flask_restless.serialization import DefaultRelationshipDeserializer
from pandas import json as ujson
from flask_restless.views.base import APIBase
from sqlalchemy import event

from pacu.core.io.scanbox.model import db as schema

original = DefaultRelationshipDeserializer.__call__
def override(self, data):
    return None if data is None else original(self, data)
DefaultRelationshipDeserializer.__call__ = override

original_smany = APIBase._serialize_many
def smany(self, instances, relationship=False):
    return original_smany(self,
        [i for i in instances if i], relationship=relationship)
APIBase._serialize_many = smany

# patching json dump
def mydumps(payload, **kwargs):
    return ujson.dumps(payload, double_precision=4)
json._json.dumps = mydumps

class nmspc:
    # '' <- memory
    session = schema.get_sessionmaker('', echo=False, autocommit=False)()
    event.listen(session, 'before_flush', schema.before_flush)
    event.listen(session, 'after_commit', schema.after_commit)

def select_db_session():
    sa = request.headers.get('pacu-jsonapi-session-arguments')
    mn = request.headers.get('pacu-jsonapi-module-name')
    nmspc.session.bind = None
    if all((sa, mn)):
        engine = importlib.import_module(mn).engine(*sa.split(','), echo=False)
        nmspc.session.bind = engine

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, PUT, POST, DELETE, HEAD, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'PACU_JSONAPI_MODULE_NAME, PACU_JSONAPI_SESSION_ARGUMENTS, PACU_JSONAPI_BASE_NAME, Content-Type'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

from pacu.core.io.scanbox.model.relationship import *

def create_endpoint():
    app = Flask(__name__)
    app.before_request(select_db_session)
    app.after_request(add_cors_headers)
    methods = 'GET POST PUT DELETE PATCH'.split()
    manager = APIManager(app=app, session=nmspc.session)
    # for orm in schema.list_orms():
    #     manager.create_api(orm, methods=methods)
    manager.create_api(Workspace, methods=methods, allow_to_many_replacement=True)
    manager.create_api(Condition, methods=methods)
    # manager.create_api(Condition, methods=methods, exclude=['trial_list'])
    # manager.create_api(Condition, methods=methods, exclude=['trials', 'trial_list'])
    manager.create_api(Trial, methods=methods)
    manager.create_api(ROI, methods=methods, exclude=['dttrialdff0s'])
    manager.create_api(Colormap, methods=methods)
    manager.create_api(DTOverallMean, methods=methods)
    manager.create_api(DTTrialDff0, methods=methods)
    manager.create_api(DTOrientationsMean, methods=methods)
    manager.create_api(DTOrientationBestPref, methods=methods)
    manager.create_api(DTAnovaEach, methods=methods)
    manager.create_api(DTOrientationsFit, methods=methods)
    manager.create_api(DTSFreqFit, methods=methods)
    manager.create_api(DTAnovaAll, methods=methods)
    manager.create_api(EphysCorrelation, methods=methods)
    manager.create_api(Action, methods=methods)
    return app
