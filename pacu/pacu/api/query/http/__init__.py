import ujson as json

from .. import __main__ as cmd # could reuse default api

def get(req, model, model_id=0, **kwargs):
    if model_id:
        data = cmd.main(model, model_id)
        return json.dumps(data)
    else:
        data = cmd.main(model)
        if isinstance(data, basestring):
            return {}
        serialized = [datum._asdict() for datum in data]
        return json.dumps(serialized)
