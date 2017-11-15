from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component

class StimulusResource(Resource):
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        pass

class StimulusBase(Component):
    __call__ = StimulusResource.bind()
