from pacu.util.inspect import repr

class Condition(object):
    def __init__(self, ori=0, sf=0, tf=0, contrast=0):
        self.ori = ori
        self.sf = sf
        self.tf = tf
        self.contrast = contrast
        self.tex = 'sin'
        self.blank = False
        self.flicker = False
        self.autoDraw = True
    __repr__ = repr.auto_strict

class RevContModCondition(object):
    def __init__(self, ori=270, sf=0, tf=1):
        self.ori = ori
        self.sf = sf
        self.tf = tf
    __repr__ = repr.auto_strict

class BlankCondition(object):
    def __init__(self, ori=0, sf=0, tf=1):
        self.ori = ori
        self.sf = sf
        self.tf = tf
        self.contrast = 1
        self.blank = True
        self.flicker = False
        self.autoDraw = False
    __repr__ = repr.auto_strict

class FlickerCondition(object):
    def __init__(self, ori=0, sf=0, tf=1):
        self.ori = ori
        self.sf = sf
        self.tf = tf
        self.contrast = 1
        self.blank = False
        self.flicker = True
        self.autoDraw = True
    __repr__ = repr.auto_strict
