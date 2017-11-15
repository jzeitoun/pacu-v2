import uuid
import base64
import functools

from tornado import web
from tornado import netutil
from tornado import process
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from ...util import identity
from ...util.concurrent import thread
from .httputil.request import Request

secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

class RequestHandler(web.RequestHandler):
    url = ''
    @classmethod
    def as_spec(cls):
        return cls.url, cls, (
            cls.initializer if hasattr(cls, 'initializer') else {})

class FrontendProxyBase(web.StaticFileHandler):
    @classmethod
    def extend(cls, root):
        return type('FrontendProxy', (cls,), dict(root=root))
    def initialize(self):
        self.get = functools.partial(self.get, 'index.html')

class Application(web.Application):
    host = None # some
    port = None # optional
    ptag = None # fields
    future = None
    @classmethod
    def get_ember_frontend_setting(cls):
        root = identity.path.ember
        FrontendProxy = FrontendProxyBase.extend(root=str(root))
        settings = dict(
            default_handler_class = FrontendProxy,
            static_path = root.joinpath('assets').str,
            static_url_prefix = '/%s/' % 'assets',
        )
        return settings
    @classmethod
    def backend(cls, handlers, **kwargs):
        specs = [handler.as_spec() for handler in handlers]
        defualt_settings = dict(
            debug=True, cookie_secret=secret,
            **cls.get_ember_frontend_setting())
        return cls(specs, **dict(defualt_settings, **kwargs))
    def run_thread(self, port=None):
        """Useful method for quick development using CLI."""
        port = port or self.port or 80
        loop = IOLoop.current()
        self.listen(port)
        self.future = thread.single.atexit(loop.stop).submit(loop.start)
        self.req = Request.with_localport(port)
        return self
    def run(self, port=None):
        port = port or self.port or 80
        try:
            sockets = netutil.bind_sockets(port)
            server = HTTPServer(self)
            server.add_sockets(sockets)
            loop = IOLoop.current()
            loop.start()
        except KeyboardInterrupt:
            server.close_all_connections()
            for socket in sockets:
                socket.close()
            loop.clear_current()
            loop.clear_instance()
            return self
    def format_status(self):
        return 'server process `{0.ptag}`' \
               ' running on {0.host}:{0.port}...'.format(self)
