import ujson

from pacu import profile
from pacu.core.model import Base
from pacu.ext.sqlalchemy.orm import session

DB = profile.manager.get('db')

def get_model(tablename):
    Models = [
        Model
        for Model in Base._decl_class_registry.values()
        if hasattr(Model, '__tablename__')
        and Model.__tablename__ == tablename]
    return Models[0] if Models else None
def parse(keys, vals, type, name):
    payload = {}
    data = dict(zip(keys, vals))
    payload['%s_name' % type] = name
    payload['%s_data' % type] = data
    return payload
def post(req, table_name, payload=()):
    kwargs = {}
    for spec in ujson.loads(payload):
        kwargs.update(parse(**spec))
    s = session.get_scoped(DB.instance())
    Model = get_model(table_name)
    model = Model(**kwargs)
    s.add(model)
    try:
        s.commit()
    except Exception as e:
        raise e
    else:
        return model.serialize()
