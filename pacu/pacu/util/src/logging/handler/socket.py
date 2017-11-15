from __future__ import absolute_import

from logging.handlers import SocketHandler
from logging.handlers import DEFAULT_TCP_LOGGING_PORT

def make(host='localhost'):
    return SocketHandler('localhost', DEFAULT_TCP_LOGGING_PORT)
