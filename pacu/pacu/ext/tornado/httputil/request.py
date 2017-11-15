import urllib

from tornado.httpclient import HTTPClient
from tornado.httpclient import HTTPRequest

class Request(object):
    host = 'localhost'
    user_agent = 'RequestMock'
    port = 80
    @classmethod
    def with_localport(cls, port):
        self = cls()
        self.port = port
        self.client = HTTPClient(force_instance=True)
        return self
    @classmethod
    def with_host_and_port(cls, host, port):
        self = cls()
        self.host = host
        self.port = port
        self.client = HTTPClient(force_instance=True)
        return self
    # TODO: extraction
    def head(self, resource=''):
        req = HTTPRequest(
            'http://{s.host}:{s.port}/{resource}'.format(
                s=self, resource=resource),
            user_agent = self.user_agent,
            method = 'HEAD'
        )
        return self.client.fetch(req)
    def get(self, resource='', timeout=10):
        req = HTTPRequest(
            'http://{s.host}:{s.port}/{resource}'.format(
                s=self, resource=resource),
            user_agent = self.user_agent,
            method = 'GET',
            request_timeout = timeout
        )
        return self.client.fetch(req)
    def post(self, resource='', **kwargs):
        req = HTTPRequest(
            'http://{s.host}:{s.port}/{resource}'.format(
                s=self, resource=resource),
            user_agent = self.user_agent,
            method = 'POST',
            body=urllib.urlencode(kwargs)
        )
        return self.client.fetch(req)
"""
req = Request.with_host_and_port('google.com', 80)
res = req.get()
"""
