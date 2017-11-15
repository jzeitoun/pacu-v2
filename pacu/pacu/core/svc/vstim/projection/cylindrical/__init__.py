from pacu.core.svc.vstim.projection.base import ProjectionBase
from pacu.core.svc.vstim.projection.eyepoint import EyepointX
from pacu.core.svc.vstim.projection.eyepoint import EyepointY

class CylindricalProjection(ProjectionBase):
    sui_icon = 'barcode'
    package = __package__
    warp = 'cylindrical'
    eyepoint_x = EyepointX(0.5)
    eyepoint_y = EyepointY(0.5)
