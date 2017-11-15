"""
For make PACU backend compliant with JSONAPI. Ember will use it.
"""

from pacu import profile
import ujson as json
from pacu.core.model import Base
from pacu.ext.sqlalchemy.orm import session
from pacu.core.model.analysis import AnalysisV1
from pacu.api.model.http.custom import query as cquery

DB = profile.manager.get('db')

modelmap = dict(
    analyses=AnalysisV1
)

def get(req, model, id=None, **kwargs):
    if model == 'tr-sessions':
        return json.dumps(dict(data=cquery.trajectory_sessions(id)))
    session = DB.instance()
    Model = modelmap.get(model)
    query = session.query(Model).order_by(Model.id.desc())
    if id:
        data = query.get(id).serialize(type=model)
    else:
        data = [m.serialize(type=model) for m in query.all()]
    return json.dumps(dict(data=data))

def post(req, model, **kwargs):
    data = json.loads(req.body)['data']
    attr = data['attributes']
    type = data['type']
    model = modelmap.get(type)(**attr)
    session = DB.instance()
    session.add(model)
    try:
        session.commit()
    except Exception as e:
        print e.__class__, e
        raise e
    else:
        data = model.serialize(type)
        return json.dumps(dict(data=data))
