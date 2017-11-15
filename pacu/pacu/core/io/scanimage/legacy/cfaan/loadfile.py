# -*- coding: utf-8 -*-
"""
Created on Sat Oct 05 16:38:36 2013

@author: kyle
"""
from __future__ import division # Enable the new behaviour
import types
from numpy import shape
import scipy #SPG 072414 used to write out motion corrected image tseries to matlab for further processing
import tifffile
from windows import TiffFig
from driftcorrect import getdrift3, driftcorrect
import cPickle as pickle
import os, time
from glamsinterface.connect import db, db2
import numpy as np
from conditions_importer import upload
from model.sfreq_meta import SpatialFrequencyMeta
from PyQt4.QtGui import QAction
from functools import partial
from ext.console import debug
from ext import console
from ext import roi_table
from ext.window.rmax_by_sfreq import RMaxBySpatialFrequencyFig
from ext.window.stats import StatsWindow
from ext.fcanvas.sfreq import TuningCurveCanvas

def getInfoFromPath(path):
    '''
    This uses the path to return a dictionary containing:
    date - a python date object
    datestr - a string of the date of the format 2014-01-31
    experimenter - a string with the experimenter name as it is in GLAMS
    experimenter_id - an int with the experimenter id as it is in GLAMS
    mouse_name - a string with the mouse name as it is in GLAMS.  If the mouse_name is not in the path, it is a 'None' object
    mouse_id an int with the experimenter id as it is in GLAMS.
    filename - the name of the tif file without the path or the extension

    The path must be either of the form
    "somewhere/experimenter/date/mouse_name/filename.tif"
    or
    "somewhere/experimenter/year.month.day/filename.tif"

    If there is no mouse_name in the path, the experimenter, date, and filename must be unique in ED (the Experiment Database).  If it is not, an error will be thrown.
    '''
    d=dict()
    d['path']=path
    path=path.split('/')
    d['filename']=path[-1].split('.tif')[0]
    try:
        d['date']=time.strptime(path[-2],'%Y.%m.%d')
    except ValueError: #if index -2 is a mousename and not a date
        d['mouse_name']=path[-2]
        d['date']=time.strptime(path[-3],'%Y.%m.%d')
        mnameExists=True
    else:
        d['mouse_name']=None
        mnameExists=False
    d['datestr']=time.strftime('%Y-%m-%d',d['date'])
    if mnameExists:
        d['experimenter']=path[-4]
    else:
        d['experimenter']=path[-3]

    # debug.enter()

    if mnameExists is False:
        ans=db.execute("""
            SELECT mice.id, lab_members.id AS experimenter_id, mice.name AS mouse_name
            FROM experiments
            LEFT JOIN mice ON mice.id=mouse_id
            LEFT JOIN lab_members ON experiments.lab_member_id=lab_members.id
            WHERE lab_members.name=%s
            AND experiments.date=%s""",(d['experimenter'], d['datestr']))
        if ans==[]:
            print('No GLAMS entry for an experiment by {} on {}'.format(d['experimenter'], d['datestr']))
            return False
        if len(ans)>1:
            print('Multiple GLAMS entries for experiments by {} on {}. Add a mouse_name to the path of this file.'.format(d['experimenter'], d['datestr']))
            return False
        else:
            d['mouse_name']=ans[0][2]
    else:
        ans=db.execute("""
            SELECT mice.id, lab_members.id AS experimenter_id
            FROM experiments
            LEFT JOIN mice ON mice.id=mouse_id
            LEFT JOIN lab_members ON experiments.lab_member_id=lab_members.id
            WHERE lab_members.name=%s
            AND experiments.date=%s
            AND mice.name=%s""",(d['experimenter'], d['datestr'], d['mouse_name']))
        if ans==[]:
            print('No glams entry for an experiment by {} on mouse {} on {}'.format(d['experimenter'], d['mouse_name'],d['date']))
            return False
    d['mouse_id']=ans[0][0]
    d['experimenter_id']=ans[0][1]
    print('Experimenter = {}\nDate of Recording = {}\nMouse name = {}\nFile name = {}'.format(d['experimenter'],d['datestr'],d['mouse_name'],d['filename']))
    return d

def getConditions(experimenter_id,date,mouse_id,filename): #experimenter='Kyle',date='2014-01-09',mouse_name='m.131207.8',filename='gcamp6-flex-visstim005'
    db2.config['database']='ed'
    c=db2.execute(""" SELECT * FROM 2P_visual_stims WHERE mouse_id=%s AND experimenter_id=%s AND date=%s AND filename=%s""",(mouse_id,experimenter_id, date,filename))
    db2.config['database']='glams'
    if c==[]:
        print("Attempting to upload the conditions file to the Experiment Database...")
        upload(experimenter_id,date,mouse_id,filename)
        db2.config['database']='ed'
        c=db2.execute(""" SELECT * FROM 2P_visual_stims WHERE mouse_id=%s AND experimenter_id=%s AND date=%s AND filename=%s""",(mouse_id,experimenter_id, date,filename))
        db2.config['database']='glams'
        if c==[]:
            print("Conditions file could not be uploaded to ED.")
            return None
    c=c[0]
    c['orientations']               =[float(orient) for orient in c['orientations'].split(',')]
    c['spatial_frequencies']        =[float(orient) for orient in c['spatial_frequencies'].split(',')]
    c['temporal_frequencies']       =[float(orient) for orient in c['temporal_frequencies'].split(',')]
    c['contrasts']                  =[float(orient) for orient in c['contrasts'].split(',')]
    c['view_angles_horiz']          =[float(orient) for orient in c['view_angles_horiz'].split(',')]
    c['view_angles_horiz_offset']   =[float(orient) for orient in c['view_angles_horiz_offset'].split(',')]
    c['sequence']                   =[int(orient)   for orient in c['sequence'].split(',') if orient!='']
    c['ontimes_S']                  =[float(orient) for orient in c['ontimes_S'].split(',')]
    c['ontimes_F']                  =[float(orient) for orient in c['ontimes_F'].split(',')]
    return c

def loadfile(maingui):
    # remove old figures if there are any
    try:
        maingui.tiffFig.traceFig.deleteLater()
        maingui.tiffFig.responseFig.deleteLater()
        maingui.roi_table.deleteLater()
        maingui.rmax_by_sfreq.deleteLater()
    except Exception:
        pass

    settings=maingui.settings
    #### get conditions from ED ####
    d=getInfoFromPath(settings.d['filename'])
    maingui.persistant=dict()
    maingui.persistant['experimenter_id']=d['experimenter_id']
    maingui.persistant['date']=d['datestr']
    maingui.persistant['mouse_id']=d['mouse_id']
    maingui.persistant['filename']=d['filename']
    if d is False: #if there was an error loading the conditions file
        maingui.conditions=None
    else:
        maingui.conditions=getConditions(experimenter_id=d['experimenter_id'],date=d['datestr'], mouse_id=d['mouse_id'],filename=d['filename'])

    ###  try loading previous results from ED ###
    ids=[maingui.persistant['mouse_id'],maingui.persistant['experimenter_id'],maingui.persistant['date'],maingui.persistant['filename']]
    db.config['database']='ed'
    ans=db.execute("SELECT data, id FROM analysis2p WHERE mouse_id=%s AND experimenter_id=%s AND date=%s and filename=%s",tuple(ids))
    db.config['database']='glams'
    if len(ans)>0:
        old_persistant=pickle.loads(ans[0][0])
        maingui.persistant=dict(maingui.persistant.items() + old_persistant.items())
        maingui.persistant['id'] = ans[0][1]
        print('Found persistent data on ED')
    else:
        maingui.persistant['id'] = None
        maingui.persistant=dict(maingui.persistant.items() + dict.fromkeys(['motionVectors','ROIs','neuropil_radius','alpha']).items())
        print('Persistent data on ED not found. This file has not been loaded into ceilingfaan before.')
    maingui.statusBar().showMessage('Loading tiff')
    t=time.time()
    tif=tifffile.TIFFfile(settings.d['filename'])
    tiffstack = tif.asarray()
    tif.close()
    tiffstack=np.transpose(tiffstack,(0,2,1))
    maingui.statusBar().showMessage('Tiff successfully loaded ({} s)'.format(time.time()-t))
    maingui.roi_table = roi_table.make_widget(maingui, show=True)

    maingui.rmax_by_sfreq = TuningCurveCanvas((536, 33, 446, 300))
    maingui.rmax_by_sfreq.show()
    maingui.stats = StatsWindow.from_geo(maingui, 680, 373, 230, 660)
    maingui.stats.show()

    # maingui.rmax_by_sfreq = RMaxBySpatialFrequencyFig()
    # maingui.rmax_by_sfreq.show()
    ## maingui.npplot = maingui.neuropil_mask.addPlot()
    ## maingui.npplot.hideAxis('left')
    ## maingui.npplot.hideAxis('bottom')

    ##########################################################
    # Injected by Hyungtae Kim <hyungtk@uci.edu>, in Nov 2014, Feb 2015
    # organize a menu to select a specific frequency based on conditions.
    #
    def on_tfreq_change(maingui, agroup):
        checked = agroup.checkedAction()
        checked_index = agroup.children().index(checked)
        maingui.tiffFig.temporal_frequency_changed(checked_index)
    def on_sfreq_change(maingui, agroup):
        checked = agroup.checkedAction()
        checked_index = agroup.children().index(checked)
        maingui.tiffFig.spatial_frequency_changed(checked_index)

    sf_agroup = maingui.sfreq_action_group
    sf_handler = partial(on_sfreq_change, maingui, sf_agroup)

    tf_agroup = maingui.tfreq_action_group
    tf_handler = partial(on_tfreq_change, maingui, tf_agroup)

    for action in sf_agroup.children():
        sf_agroup.removeAction(action)

    for action in tf_agroup.children():
        tf_agroup.removeAction(action)

    if maingui.conditions:
        maingui.sfreq_meta = SpatialFrequencyMeta(maingui.conditions)
        for index, text in enumerate(
            map(str, maingui.sfreq_meta.sfrequencies)):
            if_first = not index

            action = QAction(
                text, sf_agroup, checkable=True, checked=if_first
            )
            sf_agroup.addAction(action)
            maingui.sfreq_menu.addAction(action)
            action.triggered[()].connect(sf_handler)

        for index, text in enumerate(
            map(str, maingui.sfreq_meta.tfrequencies)):
            if_first = not index

            action = QAction(
                text, tf_agroup, checkable=True, checked=if_first
            )
            tf_agroup.addAction(action)
            maingui.tfreq_menu.addAction(action)
            action.triggered[()].connect(tf_handler)
    else:
        maingui.sfreq_meta = None

    channels=[]
    if settings.d['nChannels']==1:
        channels.append(tiffstack)
        (mt,my,mx)=shape(channels[0])
        tiffstack=np.concatenate((channels[0][...,np.newaxis],np.zeros((mt,my,mx,2))),axis=3) #this always assumes the only color is green
    elif settings.d['nChannels']==2:
        channels.append(tiffstack[0::2])
        channels.append(tiffstack[1::2])
        (mt,my,mx) = shape(channels[0])
        arr1 = channels[0][..., np.newaxis]
        arr2 = channels[1][..., np.newaxis]
        arr3 = np.zeros((mt,my,mx,1))
        tiffstack = np.concatenate((arr1, arr2, arr3), axis=3) #this always assumes the only two colors are red and green
    elif settings.d['nChannels']==3:
        channels.append(tiffstack[0::3])
        channels.append(tiffstack[1::3])
        channels.append(tiffstack[2::3])
        tiffstack=np.concatenate((channels[0][...,np.newaxis],channels[1][...,np.newaxis],channels[2][...,np.newaxis]),axis=3) #this always assumes the only three colors are red,green, and blue in that order

    COI=channels[settings.d['channelOfInterest']-1] #channel of interest
    (mt,my,mx)=shape(COI)

    if settings.d['motionCorrect']: #True or False depending on user settings
        maingui.statusBar().showMessage('Performing motion correction...')
        t=time.time()
        if maingui.persistant['motionVectors'] is None:
            print 'motion vector not found, get drift !'
            maingui.persistant['motionVectors']=getdrift3(COI)
        print 'driftcorrect...',
        tiffstack=driftcorrect(tiffstack,maingui.persistant['motionVectors'])
        print 'done !'
        maingui.statusBar().showMessage(
                'Finished motion correction ({} seconds)'.format(time.time()-t))
    else:
        maingui.statusBar().showMessage('Motion Correction is Off')
        maingui.persistant['motionVectors']=None
    tiffFig=TiffFig(tiffstack,maingui) # activates the movie display window and the response analysis windows
    # SPG 072414 writes out motion corrected file to matlab where we can save each channel as a tifstack. replace this with python
    # code once we figure out which python TIFF writer to use
    # if settings.d['saveMotionCorrectedTIFF']==True:
    #     # tiffstack.save(settings.d['filename']+'motionCorrected.tif')
    #     # tifffile.imsave(settings.d['filename']+'motionCorrected.tif',tiffstack, compress=6)
    #     matd=dict();
    #     matd['tiffStack']=tiffstack;
    #     scipy.io.savemat(settings.d['filename']+'motionCorrected.tif',matd);
    return tiffFig



def main():
    global settings
    settings=Settings()
    settings.d['filename']="D:\data\Dario\2014.11.06\w.140708.lefref\field007.tif"
    return loadfile(settings)

if __name__=='__main__':
    f=main()









