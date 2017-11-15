import importlib
import traceback
import sys

import ujson as json
from pacu.ext.tornado import websocket


def handle_exc(e):
    info = sys.exc_info()
    source = traceback.format_exception(*info)
    print '\n======== exception on websocket delegation ========'
    traceback.print_exception(*info)
    print '======== exception on websocket delegation ========\n'
    raise e

# currently web socket handler does not work in non-main thread
# thus shell mode does not support web socket in place.
class WebSocketHandler(websocket.WebSocketHandler):
    """
    A Generic web socket handler.
      * `check_origin` returns always `True`.
    """
    url = r'/socket/(?P<api>\w+)(?P<args>[\w/\.]*)'
    handler = None
    def on_message(self, message):
        # print 'ONMESSAGE', message
        try:
            payload = json.loads(message)
            # print payload, ' <-loaded'
        except ValueError as e:
            # print 'invalid json', e
            self.write_message('ERROR!'+str(e))
        else:
            try:
                event, kwargs = payload
                # print event, '<- evet'
                # print kwargs, '<-kw'
                getattr(self.handler, event)(**kwargs)
            except ValueError as e:
                # print 'invalid protocol like [`event`, `kwargs`]', e
                # self.handler.write_console('errors: ' + str(e))
                # self.write_message('ERROR!'+str(e))
                handle_exc(e)
            except Exception as e:
                # print 'error during fetching', e
                # self.handler.write_console('errors: ' + str(e))
                # self.write_message('ERROR!'+str(e))
                handle_exc(e)
    def open(self, api, args):
        # print 'OPEN', api, args
        try:
            # print 'try get websocket delegator'
            WebSocket = importlib.import_module(
                'pacu.api.%s.socket' % api).WebSocket
        except ImportError as e:
            raise e
        except AttributeError as e:
            raise e
        try:
            # print 'try bind websocket delegator'
            args = filter(None, args.split('/'))
            socket = WebSocket(*args)
            socket.on_open(self)
            self.handler = socket
        except Exception as e:
            print 'delegator init error', e
    def on_close(self):
        # print 'CLOSE'
        if self.handler:
            self.handler.on_close(self.close_code, self.close_reason)
    def write_as_fetch(self, name, **kwargs):
        self.write_message(json.dumps([name, kwargs]))
    def write_as_buffer(self, buffer):
        self.write_message(buffer, binary=True)
