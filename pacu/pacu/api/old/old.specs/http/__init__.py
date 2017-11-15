from pacu.core.service import inspect

def head(req, module_name):
    spec_names = inspect.dump_spec_names(module_name)
    spec_metas = inspect.dump_specs_for_ember_input(module_name)
    headers = [
        ('X-Pacu-Specs', ','.join(spec_names)),
    ] + spec_metas
    return headers
def get(req, *args, **kwargs):
    return 'GET'
