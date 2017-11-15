from pacu.core.svc.vstim.projection.base import ProjectionBase
from pacu.core.svc.vstim.projection.eyepoint import EyepointX
from pacu.core.svc.vstim.projection.eyepoint import EyepointY

class SphericalProjection(ProjectionBase):
    sui_icon = 'soccer'
    package = __package__
    warp = 'spherical'
    eyepoint_x = EyepointX(0.5)
    eyepoint_y = EyepointY(0.5)
