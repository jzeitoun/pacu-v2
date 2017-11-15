import os


from datetime import datetime

import numpy as np
from scipy import io

import ujson

from pacu.profile import manager
from pacu.ext.tornado.httputil.request import Request
from pacu.util.path import Path
from pacu.core.svc.vstim.handler.expv1 import ExpV1HandlerResource
from pacu.core.model.experiment import ExperimentV1
from pacu.core.svc.vstim.handler.base import HandlerBase
from pacu.core.svc.impl.exc import ServiceException
from pacu.core.svc.vstim.handler.sync_host import SyncHost
from pacu.core.svc.vstim.handler.sync_port import SyncPort
from pacu.core.svc.vstim.handler.exp_by import ExpBy, people

def get(req, protocol):
    url = 'msg/svc.andor.on_external/'
    print url + protocol
    try:
        json = ujson.loads(req.get(url + protocol, timeout=30).body or '{}')
        print json
    except ValueError as e:
        raise Exception('Communication error: invalid JSON format returned: ' + str(e))
    except Exception as e:
        raise Exception('Communication error: ' + str(e))
    data = json.get('data')
    error = json.get('error')
    if error:
        raise Exception(str(error))
    return data

def make_datapath(member, now):
    filedir = '{d.month}.{d.day}.{y}'.format(d=now, y=str(now.year)[2:])
    filename = ('{d.year}{d.month:02}{d.day:02}T'
            '{d.hour:02}{d.minute:02}{d.second:02}').format(d=now)
    return '/'.join((member, filedir, filename))

ip1_condpath = Path('D:', 'DropBox', 'Data', 'Conditions', 'Intrinsic')
def make_condpath(now):
    filedir = now.strftime('%d-%b-%Y')
    filename = ('{d.year}{d.month:02}{d.day:02}T'
            '{d.hour:02}{d.minute:02}{d.second:02}').format(d=now)
    filepath = ip1_condpath.joinpath(filedir)
    if not filepath.is_dir():
        os.makedirs(filepath.str)
    return filepath.joinpath(filename)
def savemat(path, params):
    io.savemat(path, params)
def make_params(monitor, clock, stimulus, window, handler, projection):
    # print monitor
    # print clock
    # print stimulus
    # print handler
    # print projection
    # projection['clsname'] == 'SphericalProjection'
    monitor = monitor['kwargs']
    clock = clock['kwargs']
    stimulus = stimulus['kwargs']
    window = window['kwargs']
    handler = handler['kwargs']
    projection = projection['kwargs']
    # {'eyepoint_x': 0.5, 'eyepoint_y': 0.5}
    duration = stimulus.get('snp_duration') or stimulus.get('on_duration')
    params = dict(
        Duration = np.array([[duration]], dtype='double'),
        WaitInterval = np.array([[clock.get('wait_time', 0)]], dtype='double'),
        snp_rotate = np.array([[0]], dtype='double')
    )
    # print 'PARAMS', params
    return params

class LegacyWidefieldHandlerResource(ExpV1HandlerResource):
    DB = manager.get('db')
    def __enter__(self):
        host = self.component.sync_host
        port = self.component.sync_port
        self.member_name = people[self.component.exp_by]['name']
        self.req = Request.with_host_and_port(host, port)
        self.synchronize()
        return super(LegacyWidefieldHandlerResource, self).__enter__()
    def dump(self, result):
        try:
            self.sync_close()
        except Exception as e:
            print 'Unable to close remote device!', type(e), e

        payload = result['payload']
        params = make_params(**payload)
        path = make_condpath(self.now)
        savemat(path.str, params)

        try:
            payload = result.pop('payload')
            model = ExperimentV1(**result)
            for key, val in payload.items():
                print key, val
                for attr in 'clsname pkgname kwargs'.split():
                    ett_attr = key + '_' + attr
                    ett_val = val.get(attr)
                    setattr(model, ett_attr, ett_val)
            session = self.DB.instance()
            session.add(model)
            session.commit()
        except Exception as e:
            print 'An exception from DB!', e
            result['error'] = str(e)
        else:
            result.update(id=model.id, created_at=model.created_at)

        return result
    def synchronize(self):
        # return
        self.sync_state()
        self.sync_metadata()
        self.sync_open()
    def sync_state(self):
        return get(self.req, 'state_check')
    def sync_metadata(self):
        self.now = datetime.now()
        path = make_datapath(self.member_name, self.now)
        return get(self.req, 'sync_metadata/{}'.format(path))
    def sync_open(self):
        return get(self.req, 'open')
    def sync_close(self):
        return get(self.req, 'close')

class LegacyWidefieldHandler(HandlerBase):
    sui_icon = 'database'
    package = __package__
    description = ("This handler is setup to comply the "
        "legacy widefield experiment environment that requires "
        "`tcim` and `PsychStimController`. This handler should be "
        "able to access a local machine's directory. "
        "(D/DropBox/Data/Conditions/...) It also does same thing "
        "for ExpV1 handler.")
    __call__ = LegacyWidefieldHandlerResource.bind('stimulus', 'result')
    sync_host = SyncHost('128.200.21.73')
    sync_port = SyncPort('8761')
    exp_by = ExpBy('kirstie')
    keyword = '__legacy_widefield_handler__'

# d = dict(
# Duration = np.array([[10]], dtype='double'),
# WaitInterval = np.array([[13]], dtype='double'),
# snp_rotate = np.array([[0]], dtype='double')
# )
