# Written by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014

import ipdb
from PyQt4.QtCore import pyqtRemoveInputHook

on = False

class Debugger(object):
    @property
    def enter(self):
        global on
        if on:
            pyqtRemoveInputHook()
            return ipdb.set_trace
        else:
            print 'console flag is down. skip entering debugger'
            return lambda: None

debug = Debugger()
