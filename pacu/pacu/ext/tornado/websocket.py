from tornado import websocket

class WebSocketHandler(websocket.WebSocketHandler):
    url = ''
    @classmethod
    def as_spec(cls):
        return cls.url, cls,
    def check_origin(self, origin):
        return True
