from cStringIO import StringIO

import numpy as np
import psychopy.logging

from pacu.profile import manager
from pacu.core.svc.impl.exc import UserAbortException
from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component
from pacu.core.svc.vstim.handler.exp_on import ExpOn
from pacu.core.svc.vstim.handler.exp_by import ExpBy
from pacu.core.svc.vstim.handler.exp_note import ExpNote

class HandlerResource(Resource):
    def __enter__(self):
        self.log = psychopy.logging.LogFile(StringIO())
        return self
    def service_done(self, service):
        trials = self.stimulus.trials
        try:
            trial_list = np.array([vars(t.condition) for t in trials.trialList])
        except:
            trial_list = np.array([])
        self.result.update(
            clsname = type(service).__name__,
            pkgname = type(service).__module__,
            payload = service.as_payload,
            message = self.log.stream.getvalue(),
            sequence = list(trials.sequenceIndices),
            trial_list = trial_list,
            **{k: v.filled().tolist() for k, v in trials.data.items()})
        return self.result

class HandlerBase(Component):
    exp_on = ExpOn()
    exp_by = ExpBy('anonymous')
    # exp_note = ExpNote('')
    __call__ = HandlerResource.bind('stimulus', 'result')
