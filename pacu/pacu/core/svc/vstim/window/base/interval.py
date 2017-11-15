from psychopy.core import StaticPeriod

class Interval(object):
    def __init__(self, win):
        frameRate = win.getActualFrameRate() # could be None. What then ?
        self.frameRate = frameRate / 2
        self.frameDuration = 1.0/round(self.frameRate)
        self.win = win
        self.isi = StaticPeriod(screenHz=self.frameRate, win=win)
    def start(self):
        self.isi.start(self.frameDuration)
    def complete(self):
        self.isi.complete()

