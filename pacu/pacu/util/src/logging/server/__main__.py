from __future__ import absolute_import

import atexit
import struct
import socket
import pickle
from logging import makeLogRecord
from logging.handlers import DEFAULT_TCP_LOGGING_PORT

from .. import get_default

logger = get_default()
logger.info('TCP server is configured to stream log...')
def log_by_object(log_object):
    logger.handle(makeLogRecord(log_object))

HOST = 'localhost'
PORT = DEFAULT_TCP_LOGGING_PORT

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
atexit.register(s.close)

def loop(s):
    conn, addr = s.accept()
    atexit.register(conn.close)
    while True:
        head = conn.recv(4)
        if len(head) < 4:
            break
        length = struct.unpack('>L', head)[0]
        chunk = conn.recv(length)
        while len(chunk) < length:
            chunk = chunk + conn.recv(length - len(chunk))
        log_by_object(pickle.loads(chunk))

if __name__ == '__main__':
    try:
        while True:
            print
            loop(s)
            print
    except BaseException as e: # including keyboard interrupt
        pass
