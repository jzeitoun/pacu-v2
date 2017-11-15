from psychopy import core
from psychopy import misc
from psychopy.visual.windowwarp import Warper
from psychopy.monitors import Monitor
from psychopy.visual.grating import GratingStim
from psychopy.visual.window import Window

mon = Monitor('GenericMonitor', width=33.169, distance=10)
mon.setSizePix((1440, 900))
win = Window((1440, 900), monitor=mon, fullscr=True, useFBO=True, allowStencil=True)
warper = Warper(win, warp='spherical', warpGridsize=300, eyepoint=[0.5, 0.5])
stim = GratingStim(win=win, units='deg', tex='sin', sf=0.1,
    size = misc.pix2deg(win.size, win.monitor)
)
print win.size
print 'win size', win.size
print 'mon size', win.monitor.getSizePix()
print 'as deg', misc.pix2deg(win.size, win.monitor)
stim.draw()
win.flip()
core.wait(0.5)
win.close()
