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

def post(req, table_name, **payload):
    s = session.get_scoped(DB.instance())
    Model = get_model(table_name)
    model = Model(**payload)
    s.add(model)
    try:
        s.commit()
    except Exception as e:
        raise e
    else:
        return model.serialize()
