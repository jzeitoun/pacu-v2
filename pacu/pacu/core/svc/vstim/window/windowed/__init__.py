from pacu.core.svc.vstim.window.base import WindowBase
from pacu.core.svc.vstim.window.pixel_x import PixelX
from pacu.core.svc.vstim.window.pixel_y import PixelY

class Window(WindowBase):
    package = __package__
    sui_icon = 'browser'
    pixel_x = PixelX(400)
    pixel_y = PixelY(960)
    fullscr = False
