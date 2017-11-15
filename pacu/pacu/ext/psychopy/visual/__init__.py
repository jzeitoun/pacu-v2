import pyglet
import numpy as np

from pyglet import window
from pyglet.window import Window as GenericPyGletWindow
from psychopy.visual import Window as PsychopyWindow

class GhostPygletWindow(GenericPyGletWindow):
    def __init__(self, *args, **kwargs):
        kwargs['visible'] = False
        super(GhostPygletWindow, self).__init__(*args, **kwargs)

class GhostWindow(PsychopyWindow):
    def __init__(self, *args, **kwargs):
        window.Window = GhostPygletWindow
        super(GhostWindow, self).__init__(*args, **kwargs)
        self.buftype = (pyglet.gl.GLubyte * (4 * self.size.prod()))
        window.Window = GenericPyGletWindow
    def backbuf_to_bytes(self):
        ghostbuf = self.buftype()
        GL = pyglet.gl
        width, height = self.size.tolist()
        GL.glReadBuffer(GL.GL_BACK)
        GL.glReadPixels(0, 0, width, height,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, ghostbuf)
        self.clearBuffer()
        return np.frombuffer(ghostbuf, dtype='uint8').tostring() #.reshape((width, height, 4))
