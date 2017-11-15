from __future__ import print_function

import importlib

from ...util.path import Path
from ...util.format.table import simple

here = Path.absdir(__file__)
paths = [py for py in here.ls('*.py') if not py.name.startswith('_')]
names = [py.stem for py in paths]

class NoScriptError(Exception):
    pass
def get_scripts():
    header = '= Choose one of the available scripts ='
    return '\n'.join([header] + names)
def run_script(script, *args):
    module = 'pacu.api.ping.%s' % script
    try:
        ping = importlib.import_module(module).ping
    except ImportError:
        raise NoScriptError
    except AttributeError as e:
        raise Exception('Script `%s` has no `ping` method.' % script)
    try:
        return ping(*args)
    except Exception as e:
        raise Exception('Script `%s` has raised an error.\n(%s).' % (
            script, str(e)))
def main(script, *args):
    return run_script(script, *args)

if __name__ == '__api_main__':
    try:
        result = main(script, *args)
    except NoScriptError:
        result = get_scripts()
    except Exception as e:
        result = str(e)
    if isinstance(result, dict):
        print(simple.show('{}'.format(script), result.items()))
    else:
        print(result)
