from pacu.core.svc.vstim.window.base.interval import Interval
from pacu.core.svc.impl.resource import Resource
from pacu.core.svc.impl.component import Component
from pacu.core.svc.vstim.window.screen import Screen

class WindowResource(Resource):
    def __enter__(self):
        comp = self.component
        from psychopy.visual import Window # eats some time
        window = Window((comp.pixel_x, comp.pixel_y),
            useFBO = True,
            # units='deg',
            monitor = self.monitor.instance,
            allowStencil = True,
            screen = comp.screen,
            fullscr = comp.fullscr)
        self.instance = window
        self.flip = window.flip
        return self
    def __exit__(self, type, value, tb):
        self.instance.close()
    def get_isi(self):
        return Interval(self.instance)

class WindowBase(Component):
    __call__ = WindowResource.bind('monitor')
    screen = Screen(0)
    description = (
        'Screen# is set as 0 for most cases. '
        'But you can set other numbers when run a stimulus on different monitor. '
        'In most cases, screen number increases sequentially. '
        "## Author's comment ##"
        "I'm afraid that from Maveriks onwards OSX doesn't allow the second window ever to be in true full-screen mode. "
    )
