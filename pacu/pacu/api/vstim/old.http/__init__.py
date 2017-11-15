import ujson

from pacu.core import service

def do_stim(*specs):
    Service = service.from_module('pacu.core.service.vstim.gratings')
    for spec in specs:
        spec_type = spec.pop('type')
        spec_name = spec.pop('name')
        spec_attr = getattr(Service, spec_type)
        kwargs = dict(zip(spec['keys'], spec['vals']))
        spec_attr(spec_name, **kwargs)
    srv = Service()
    return srv.run()

def post(req, payload="{}"):
    payload = ujson.loads(payload)
    data = do_stim(*payload)
    return data
    return dict(
        code=200
    )
