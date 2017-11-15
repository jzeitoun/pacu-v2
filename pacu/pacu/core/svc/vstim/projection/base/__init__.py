from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component

class ProjectionResource(Resource):
    def __enter__(self):
        from psychopy.visual.windowwarp import Warper # eats some time
        comp = self.component
        projection = Warper(self.window.instance, warp=comp.warp,
            warpGridsize=300,
            eyepoint=[comp.eyepoint_x, comp.eyepoint_y])
        self.instance = projection
        return self

class ProjectionBase(Component):
    __call__ = ProjectionResource.bind('window')
