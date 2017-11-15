import socket

from pacu.ext.psychopy import logging
from pacu.core.svc.impl.exc import TimeoutException
from pacu.core.svc.vstim.clock.base import ClockResource
from pacu.core.svc.vstim.clock.base import ClockBase
from pacu.core.svc.vstim.clock.port import Port
from pacu.core.svc.vstim.clock.timeout import Timeout
from pacu.core.svc.vstim.clock.dest_ip import DestIP

class TwowayTCPClockResource(ClockResource):
    def synchronize(self, stimulus):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', self.component.port))
        s.listen(1)
        s.settimeout(self.component.timeout)
        await_msg = 'Await signal for %s sec(s)...' % self.component.timeout
        logging.msg(await_msg)
        logging.flush()
        stimulus.flip_text(await_msg)
        try:
            conn, addr = s.accept() # block!
            try:
                data = conn.recv(0) # just for faster response
            except Exception as e:
                print 'ERROR FROM RECV', str(e)
            self.wait(stimulus)
            # now = time.time()
            # conn.send(str(now))
            conn.close()
        except socket.timeout:
            raise TimeoutException
        finally:
            s.close()

class TwowayTCPClock(ClockBase):
    sui_icon = 'wait'
    package = __package__
    dest_ip = DestIP('127.0.0.1')
    dest_port = Port(12345, title='Destination Port')
    port = Port(12345)
    timeout = Timeout(10)
    __call__ = TwowayTCPClockResource.bind()
    description = '''
        This clock is synchronized in two way.
        First the clock sends duration of current stimulus
        to the destination ip and waits for
        a callback packet. After synchronization,
        the clock will wait another amount of time set in wait time.
    '''
