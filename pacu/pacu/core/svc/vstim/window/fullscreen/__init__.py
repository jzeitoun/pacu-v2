from pacu.core.svc.vstim.window.base import WindowBase

class Fullscreen(WindowBase):
    sui_icon = 'maximize'
    package = __package__
    pixel_x = 0
    pixel_y = 0
    fullscr = True
