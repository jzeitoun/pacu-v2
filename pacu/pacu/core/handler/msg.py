import importlib
from collections import defaultdict

from ...ext.tornado.web import RequestHandler

gets = defaultdict(list)
posts = defaultdict(list)

class MSGHandler(RequestHandler):
    url = r'/msg/(?P<msg>[\w\-\.]+)(?P<args>[\w/\-\.]*)'
    def prepare(self):
        try:
            msg = self.path_kwargs['msg']
            args = self.path_kwargs['args']
            self.args = filter(None, args.split('/'))
            self.kwargs = {key: val
                for key, vals in self.request.arguments.items()
                for val in vals}
        except KeyError:
            self.send_error(400)
        except Exception as e:
            self.send_error(500)
    def get(self, msg, args):
        # print 'get', msg, args, gets[msg]
        for handler in gets[msg]:
            handler(self, *self.args, **self.kwargs)
    def post(self, msg, args):
        for handler in posts[msg]:
            handler(self, *self.args, **self.kwargs)
