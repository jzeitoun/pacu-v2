import cPickle
from datetime import datetime

from pacu.util import identity
from pacu.profile import manager
from pacu.core.model.experiment import ExperimentV1
from pacu.core.svc.vstim.handler.base import HandlerResource
from pacu.core.svc.vstim.handler.base import HandlerBase
from pacu.core.svc.vstim.handler.keyword import Keyword

class ExpV1HandlerResource(HandlerResource):
    DB = manager.get('db')
    def __enter__(self):
        super(ExpV1HandlerResource, self).__enter__()
        if not self.component.keyword:
            raise Exception('Keyword (filename of the recording) can not be empty.')
        return self
    def service_done(self, service):
        result = super(ExpV1HandlerResource, self).service_done(service)
        return self.dump(result)
    def dump(self, result): # to DB
        try:
            payload = result.pop('payload')
            model = ExperimentV1(**result)
            for key, val in payload.items():
                for attr in 'clsname pkgname kwargs'.split():
                    ett_attr = key + '_' + attr
                    ett_val = val.get(attr)
                    setattr(model, ett_attr, ett_val)
            off_duration = model.stimulus_kwargs.get('off_duration')
            model.keyword = self.component.keyword
            model.duration = max(t for ts in model.off_time for t in ts) + off_duration
            session = self.DB.instance()
            session.add(model)
            session.commit()
        except Exception as e:
            print 'An exception from DB!', e
            result['errormsg'] = str(e)
            result['errortype'] = type(e)
            raise e
        else:
            result.update(id=model.id, created_at=model.created_at)
        finally:
            vispath = identity.path.userenv.joinpath('visstim')
            vispath.mkdir_if_none()
            ftime = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
            logfile = '{}.{}.pickle'.format(ftime, self.component.keyword.replace('/', '_'))
            logpath = vispath.joinpath(logfile)
            with logpath.open(mode='wb') as f:
                cPickle.dump(dict(
                    payload=payload, result=result, keyword=self.component.keyword
                ), f)
        return result

class ExpV1Handler(HandlerBase):
    sui_icon = 'database'
    package = __package__
    description = 'Users must provide a correct information (filename, path, etc...) of recordings to be used for search later in analysis session.'
    __call__ = ExpV1HandlerResource.bind('stimulus', 'result')
    keyword = Keyword('')
