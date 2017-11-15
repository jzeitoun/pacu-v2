import time

import psychopy.logging

from pacu.core.svc.vstim import VisualStimulusService

class ConsolePipe(list):
    def write(self, message):
         return [writer(message) for writer in self]

pipe = ConsolePipe()
psychopy.logging.LogFile(pipe)

class WebSocket(object):
    def on_open(self, socket):
        # print 'ON_OPEN DELE'
        try:
            self.write_as_fetch = socket.write_as_fetch
            self.write_as_buffer = socket.write_as_buffer
        except Exception as e:
            print e
        # print 'end of on open'
    def on_close(self, code, reason):
        pass
        # print 'ON CLOSE DELE'
    def run(self, **payload):
        if not payload:
            return self.write_console('Empty payload can not initiate services.')
        try:
            service = VisualStimulusService.from_payload(**payload)
        except Exception as e:
            self.write_console('Failed to initialize service.')
            self.write_console(str(e))
        else:
            self.run_service(service)
    def run_service(self, service):
        pipe.append(self.write_console)
        result = service() or {}
        pipe.remove(self.write_console)
        self.write_as_fetch('svcComplete', **result)
    def write_console(self, messages, context='info'):
        epoch = time.time()
        for message in messages.splitlines():
            self.write_as_fetch('addMessage',
                epoch = epoch,
                body = message,
                context = context
            )
