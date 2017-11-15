from pacu.profile import manager
from pacu.core import model as m
from pacu.core.model import fixture as f
from pacu.util import identity as i

manager.print_status()
db, log, web, opt = manager.instances('db', 'log', 'web', 'opt')

try:
    app = web.run_thread()
    log.debug(app.format_status())
except Exception as e:
    log.warn('Failed to run app. ({!s})'.format(e))

if __name__ == '__api_main__':
    banner = 'This shell has some predefined variables. Type `whos` to look up.\n'
    try:
        import IPython
        IPython.embed(banner2=banner, user_ns=globals())
    except ImportError as e:
        import code
        code.InteractiveConsole(globals()).interact()
    except Exception as e:
        import traceback
        print 'Unable to launch a shell instance. Check following error.'
        print type(e), e
