# -*- coding: utf-8 -*-
"""
Created on Wed Dec 11 08:28:18 2013

@author: kyle

This code uses PyQt4 for the GUI and pyqtgraph for graphing.
"""
from __future__ import division # Enable the new behaviour
import sys, os, types, time
from PyQt4.QtGui import QActionGroup
from PyQt4.QtGui import QAction
from PyQt4 import QtGui, QtCore  # Qt is Nokias GUI rendering code written in C++.  PyQt4 is a library in python which binds to Qt
from PyQt4 import uic
from loadfile import loadfile
import cPickle as pickle # pickle serializes python objects so they can be saved persistantly.  It converts a python object into a savable data structure
from glamsinterface.connect import db, db2

from windows import TiffFig
from ext.console import debug
from functools import partial

os.chdir(os.path.split(os.path.realpath(__file__))[0])

class Settings():
    def __init__(self):
        try:
            self.d=pickle.load(open('config.p', "rb" ))
            self.d['saveMotionCorrectedTIFF']=True #SPG 072414
        except IOError:
            self.d=dict()
            self.d['motionCorrect']=True
            self.d['autodetectROIs']=False
            self.d['nChannels']=2
            self.d['channelOfInterest']=2
            self.d['channel1Color']='Red'
            self.d['channel2Color']='Green'
            self.d['channel3Color']=''
            self.d['filename']=None
            #SPG 072414 for making motion corrected stacks that can be edited in FIJI
            self.d['saveMotionCorrectedTIFF']=False
    def save(self):
        '''save to a config file.'''
        pickle.dump(self.d, open( 'config.p', "wb" ))

def initializeMainGui():
    m=uic.loadUi("gui/gui.ui")
    m.settings=Settings()
    m.setWindowTitle('ceilingfaan')
    m.actionExit.triggered.connect(QtGui.qApp.quit)
    m.actionOpen.triggered.connect(types.MethodType(getfilename,m)) # This is a way to add methods to a class after instantiation.
    m.actionSettings.triggered.connect(types.MethodType(openSettingsDialog,m))
    m.actionSave.triggered.connect(types.MethodType(saveResults,m))
    m.saveSettings=saveSettings
    m.persistant=None
    m.tiffFig=None
    m.setGeometry(QtCore.QRect(20, 372, 646, 660))

    ##########################################################
    # Injected by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014, Feb 2015
    # Providing a menu to select specific spatial frequency.
    #
    m.sfreq_menu = m.menubar.addMenu('Spatial Frequencies')
    m.tfreq_menu = m.menubar.addMenu('Temporal Frequencies')
    m.sfreq_action_group = QActionGroup(m, exclusive=True)
    m.tfreq_action_group = QActionGroup(m, exclusive=True)
    #
    m.np_comp_menu = m.menubar.addMenu('Neuropil Compensation')
    m.np_comp_action_group = QActionGroup(m, exclusive=True)
    np_actiongroup = m.np_comp_action_group

    action1 = QAction('off', np_actiongroup, checkable=True, checked=False)
    # action2 = QAction('double', np_actiongroup, checkable=True, checked=False)
    action3 = QAction('whole', np_actiongroup, checkable=True, checked=True)

    TiffFig.bind_neuropil_action(m, np_actiongroup, action1)
    # TiffFig.bind_neuropil_action(m, np_actiongroup, action2)
    TiffFig.bind_neuropil_action(m, np_actiongroup, action3)

    np_actiongroup.addAction(action1)
    # np_actiongroup.addAction(action2)
    np_actiongroup.addAction(action3)

    m.np_comp_menu.addAction(action1)
    # m.np_comp_menu.addAction(action2)
    m.np_comp_menu.addAction(action3)

    action3.trigger()
    #
    #
    ##########################################################
    # for debug
    #
    from ext.menubar import DebugMenubar
    dmenubar = DebugMenubar(m)
    debug_menu = m.menubar.addMenu('Debug')
    debug_menu.addAction('enter...'
        ).triggered[()].connect(dmenubar)
    #
    ##########################################################
    ##########################################################
    # for export
    #
    from ext.menubar import ExportMenubar
    export_menubar = ExportMenubar(m)
    export_menu = m.menubar.addMenu('Export')
    export_menu.addAction('Copy response values to clipboard...'
        ).triggered[()].connect(
            partial(export_menubar.copy_response_values_to_clipboard))
    export_menu.addAction('Copy response matrix to clipboard...'
        ).triggered[()].connect(
            partial(export_menubar.copy_response_matrix_to_clipboard))
    m.export_menubar = export_menubar
#     export_menu.addAction('Copy response values by all SF to clipboard...'
#         ).triggered[()].connect(
#             partial(export_menubar.copy_response_all_values_to_clipboard))
    #
    ##########################################################

    m.show()
    # from ext.window.neuropil import NeuropilMaskFig
    # fig = NeuropilMaskFig()
    # m.fig = fig
    # fig.show()
    # plot = fig.addPlot(title = "neuropil mask")
    # import pyqtgraph as pg
    # import numpy as np
    # arr = np.zeros((64, 64), np.uint8)
    # arr[32,:] = 255
    # item = pg.ImageItem(arr)
    # plot.addItem(item)
    # debug.enter()
    return m


def saveResults(self):
    if self.persistant is None:
        self.alert=QtGui.QMessageBox.information(self, 'Save Results',"You must load a file in order to save the results.")
    else:
        self.persistant['ROIs']=[r.getpersistant() for r in self.tiffFig.rois] #This creates a list with the numbers of interest (determined by getpersistant() for each ROI.
        p=pickle.dumps(self.persistant)
        ids=[self.persistant['mouse_id'],self.persistant['experimenter_id'],self.persistant['date'],self.persistant['filename']] #The four components of an ID (moud, experimenter, date, and filename) make a file unique.

        db.config['database']='ed'
        ans=db.execute("SELECT * FROM analysis2p WHERE mouse_id=%s AND experimenter_id=%s AND date=%s and filename=%s",tuple(ids)) #This exists to check whether this file has been analyzed before
        date_analyzed=time.strftime('%Y-%m-%d',time.localtime())
        ids.insert(0,date_analyzed)
        ids.insert(1,p)
        if len(ans)>0:
            db.execute("UPDATE analysis2p SET date_analyzed=%s, data=%s WHERE mouse_id=%s AND experimenter_id=%s AND date=%s AND filename=%s",tuple(ids))
            self.statusBar().showMessage("Results were successfully saved (Overwrote previous results).")
        else:
            db.execute("INSERT INTO analysis2p SET date_analyzed=%s, data=%s, mouse_id=%s, experimenter_id=%s, date=%s, filename=%s",tuple(ids))
            self.statusBar().showMessage    ("Results were successfully saved.")
        db.config['database']='glams'



def saveSettings(self):
    self.settings.d['motionCorrect']=bool(self.settings_ui.motionCorrect.checkState())
    self.settings.d['autodetectROIs']=bool(self.settings_ui.autodetectROIs.checkState())
    self.settings.d['nChannels']=self.settings_ui.nChannels.value()
    self.settings.d['channelOfInterest']=self.settings_ui.channelOfInterest.value()
    self.settings.d['channel1Color']=str(self.settings_ui.channel1Color.currentText())
    self.settings.d['channel2Color']=str(self.settings_ui.channel2Color.currentText())
    self.settings.d['channel3Color']=str(self.settings_ui.channel3Color.currentText())
    self.d['saveMotionCorrectedTIFF']=str(self.settings_ui.saveMotionCorrectedTIFF.currentText())
    self.settings.save()

def getfilename(self):
    if self.settings.d['filename'] is not None:
        filename= QtGui.QFileDialog.getOpenFileName(self, 'Open File', self.settings.d['filename'], '*.tif')
    else:
        filename= QtGui.QFileDialog.getOpenFileName(self, 'Open File', '*.tif')
    filename=str(filename)
    if filename=='':
        return False
    else:
        self.settings.d['filename']=filename
        self.settings.save()
        self.tiffFig=loadfile(self)
        self.setWindowTitle('ceilingfaan - {}'.format(filename))
        self.setCentralWidget(self.tiffFig)

def openSettingsDialog(self):
    a=uic.loadUi("gui/settings.ui")
    #load all the previous settings
    a.buttonBox.accepted.connect(types.MethodType(saveSettings,self))
    color2index={'Red':1,'Green':2,'Blue':3,'':-1}

    a.motionCorrect.setChecked(self.settings.d['motionCorrect'])
    a.autodetectROIs.setChecked(self.settings.d['autodetectROIs'])
    a.nChannels.setValue(self.settings.d['nChannels'])
    a.channelOfInterest.setValue(self.settings.d['channelOfInterest'])
    a.channel1Color.setCurrentIndex(color2index[self.settings.d['channel1Color']])
    a.channel2Color.setCurrentIndex(color2index[self.settings.d['channel2Color']])
    a.channel3Color.setCurrentIndex(color2index[self.settings.d['channel3Color']])
    self.settings_ui=a
    self.settings_ui.show()




if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    maingui=initializeMainGui()
    #sys.exit(app.exec_()) #uncomment required to run outside of Spyder

