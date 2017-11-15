from ..ext.tornado.web import Application
from ..core.handler.jsonapi import JSONAPIHandler
from ..core.handler.api import APIHandler
from ..core.handler.msg import MSGHandler
from ..core.handler.websocket import WebSocketHandler
from ..core.handler.ws import WSHandler
# from ..core.handler.mmwstream import MMWStreamHandler

def default(profile):
    kwargs = {
        key: getattr(profile, key) for key in [
        'twitter_consumer_key',
        'twitter_consumer_secret',
        'google_consumer_key',
        'google_consumer_secret',
        'facebook_api_key',
        'facebook_secret'
    ]}
    app = Application.backend(
        [JSONAPIHandler, APIHandler, MSGHandler,
           #  MMWStreamHandler,
        WSHandler, WebSocketHandler],
        debug = profile.debug.bool,
        compress_response = profile.compress_response.bool,
        **kwargs)
    app.host = profile.host
    app.port = profile.port.int
    app.ptag = profile.ptag
    return app
