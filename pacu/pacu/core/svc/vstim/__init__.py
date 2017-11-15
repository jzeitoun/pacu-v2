import traceback

from pacu.ext.psychopy import logging
from pacu.core.svc.impl import spec
from pacu.core.svc.impl import specs
from pacu.core.svc.impl.exc import UserAbortException
from pacu.core.svc.impl.exc import ServiceRuntimeException
from pacu.core.svc.impl.exc import TimeoutException
from pacu.core.svc.impl.exc import ComponentNotFoundError
from pacu.core.svc.impl.service import Service
from pacu.core.svc.impl.component_dependency import ComponentDependency

class VisualStimulusService(Service):
    monitor    = ComponentDependency()
    window     = ComponentDependency()
    projection = ComponentDependency()
    clock      = ComponentDependency()
    stimulus   = ComponentDependency()
    handler    = ComponentDependency()
    def __call__(self):
        with self                                     as result    ,\
             self.clock()                             as clock     ,\
             self.monitor()                           as monitor   ,\
             self.window(monitor)                     as window    ,\
             self.projection(window)                  as projection,\
             self.stimulus(window, clock, projection) as stimulus  ,\
             self.handler(stimulus, result)           as handler:
            for trial in stimulus.synced: # experiment generating
                while trial:              # inter-condition-interval
                    with trial:           # inter-stimulus-interval
                        pass              # updating screen over each frame
            else:                         # ended properly or by user
                return result
    def __enter__(self):
        clock = logging.clock.MonotonicClock()
        logging.setDefaultClock(clock)
        logging.msg('Entering visual stimulus...')
        logging.flush()
        return {} # prepared for result
    def __exit__(self, type, value, tb):
        if type is None:
            self.handler.current.service_done(self)
        elif type is UserAbortException:
            logging.msg('User aborted the session.')
        elif type is TimeoutException:
            logging.error('Timeout. Session aborted.')
        elif type is ComponentNotFoundError:
            logging.error('ComponentNotFoundError: ' + str(value))
        elif type is ServiceRuntimeException:
            trace = '\n'.join(traceback.format_tb(tb))
            logging.critical('An error occurred. ({})\n\n{}'.format(value, trace))
        else:
            trace = '\n'.join(traceback.format_tb(tb))
            logging.critical('Unknown error occurred. ({}:{})\n\n{}'.format(type, value, trace))
        logging.msg('Exiting visual stimulus...')
        logging.flush()
        return True

__all__ = specs([
    spec('monitor', 'monitors', [
        ('generic', 'GenericMonitor'),
        ('kirsties', 'KirstiesRegularMonitor'),
        ('kirsties', 'KirstiesLargeMonitor'),
        ('jacks', 'JacksRegularMonitor'),
        ('xulab', 'XuLabsPrimaryMonitor'),
        # ('example', 'ExampleComponent'),
    ]),
    spec('window', 'windows', [
        ('windowed', 'Window'),
        ('fullscreen', 'Fullscreen'),
        ('kirscreen', 'Kirscreen'),
    ]),
    spec('stimulus', 'stimuli', [
        ('gratings', 'GratingsStimulus'),
        ('gratings', 'RevContModGratingsStimulus'),
        ('sparse_noise', 'SparseNoiseStimulus'),
        ('sweeping_noise', 'SweepingNoiseStimulus'),
    ]),
    spec('projection', 'projections', [
        ('flat', 'FlatProjection'),
        ('spherical', 'SphericalProjection'),
        ('cylindrical', 'CylindricalProjection'),
    ]),
    spec('clock', 'clocks', [
        ('internal', 'InternalClock'),
        ('tcp', 'OnewayTCPClock'),
        ('tcp', 'TwowayTCPClock'),
        ('labjack', 'LabJackClock'),
        ('labjack', 'LabJackDriver'),
        ('labjack.miniscope', 'LabJackMiniscopeDriver'),
        ('labjack.scanbox', 'LabJackScanboxDriver'),
    ]),
    spec('handler', 'handlers', [
        ('dryrun', 'DryrunHandler'),
        ('expv1', 'ExpV1Handler'),
        ('legacy.widefield', 'LegacyWidefieldHandler'),
    ]),
], package=__package__, service=VisualStimulusService)
