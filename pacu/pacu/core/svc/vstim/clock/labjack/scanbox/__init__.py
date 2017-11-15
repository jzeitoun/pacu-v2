import socket

from psychopy import event
from psychopy.core import CountdownTimer

from pacu.ext.labjack.u3 import U3Proxy
from pacu.ext.psychopy import logging
from pacu.core.svc.impl.exc import ComponentNotFoundError
from pacu.core.svc.impl.exc import TimeoutException
from pacu.core.svc.impl.exc import UserAbortException
from pacu.core.svc.impl.exc import ComponentNotFoundError
from pacu.core.svc.vstim.clock.base import ClockResource
from pacu.core.svc.vstim.clock.base import ClockBase
from pacu.core.svc.vstim.clock.timeout import Timeout
from pacu.core.svc.vstim.clock.port import Port
from pacu.core.svc.vstim.clock.dest_ip import DestIP
from pacu.core.svc.vstim.clock.text import Text
from pacu.core.svc.vstim.clock.check import Check

text = 'Sent a start signal to Scanbox. Await a TTL back through LabJack in {} sec...'

class LabJackScanboxDriverResource(ClockResource): # will use psychopy clock for visstim timestamps
    def verify_component(self):
        pass
    def send_start(self):
        return self.udp.sendto('G\n', self.dest)
    def send_stop(self):
        return self.udp.sendto('S\n', self.dest)
    def __enter__(self):
        try:
            self.proxy = U3Proxy()
            self.u3 = self.proxy.__enter__()
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dest = self.component.dest_ip, self.component.dest_port
            self.verify_component()
        except Exception as e:
            raise ComponentNotFoundError(
                'Could not initialize LabJack Device: ' + str(e))
        return super(LabJackScanboxDriverResource, self).__enter__()
    def __exit__(self, type, value, traceback):
        self.send_stop()
        self.udp.close()
        self.finished_at = self.getTime() - self.started_at
        self.proxy.__exit__(type, value, traceback)
    def synchronize(self, stimulus):
        self.send_start()
        logging.msg(text.format(self.component.timeout))
        logging.flush()
        for i in range(self.component.timeout, 0, -1):
            timer = CountdownTimer(1)
            msg = text.format(i)
            stimulus.flip_text(msg)
            while timer.getTime() > 0:
                if event.getKeys('escape'):
                    raise UserAbortException()
                if self.u3.get_counter():
                    logging.msg('counter increased')
                    logging.flush()
                    # self.instance.reset_timer()
                    return
        else: # timeout...
            raise TimeoutException('Could not catch any signal from LabJack.')

description = '''
<div class="ui inverted basic segment">
  <h1 class="ui center aligned header">Scanbox</h1>
  <img class="ui fluid image" src="https://scanbox.files.wordpress.com/2014/03/cropped-sbbanner1.png"/>
  <p>This class can communicate with Scanbox API. Supported features so far;</p>
  <ul class="ui list">
    <li>Start recording</li>
    <li>Stop recording</li>
    <li>Set file path (Animal/Unit/Exp)</li>
  </ul>
</div>
'''

class LabJackScanboxDriver(ClockBase):
    sui_icon = 'lightning'
    package = __package__
    timeout = Timeout(15, description='number')
    wait_time = 0
    dest_ip = DestIP('128.200.21.221', title='Scanbox IP address', description='string')
    dest_port = Port(7000, title='Scanbox UDP port', description='number')
    override_path = Check(False, title='Override Path', tooltip="If checked, none of path information shouldn't be blank.")
    animal_name = Text('', title='Animal Name', description='path')
    unit_number = Text('', title='Unit Number', description='path')
    exp_number = Text('', title='Experiment Number', description='path')
    description = description
    __call__ = LabJackScanboxDriverResource.bind()
