from pacu.core.svc.vstim.window.base import WindowBase
from pacu.core.svc.vstim.window.screen import Screen

class Kirscreen(WindowBase):
    sui_icon = 'maximize'
    package = __package__
    pixel_x = 0
    pixel_y = 0
    fullscr = True
    screen = Screen(2)
    description = ("This is your preset, Kirstie! "
        "Make sure that the large monitor is currently active.")
