import ujson

from .. import __main__ as cmd # could reuse default api

def get(ping, script, *args):
    data = cmd.main(script, *args)
    return ujson.dumps(data)
