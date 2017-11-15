import atexit

from concurrent.futures import ThreadPoolExecutor

"""
from tornado.ioloop import IOLoop
loop = IOLoop.current()
future = single.atexit(loop.stop).submit(loop.start)
"""

class SelfClosingExecutor(ThreadPoolExecutor):
    def atexit(self, func):
        atexit.register(func)
        return self

single = SelfClosingExecutor(1)
