# -*- coding: utf-8 -*-
"""
Created on Thu Jan 02 09:03:31 2014
@author: Kyle Ellefsen

This file will look through all the files on the NAS, find the corresponding experiments in GLAMS, and add the experiment metadata to ED (Experiment Database).

Instructions
============
*) Make sure the Data folder on the NAS is mounted on Z:\ (if it isn't, change the variable 'pathTo2P')
   To do this: Open Windows Explorer, right click 'Network', click 'Map Network Drive',  select Drive='X:' and Folder='\\128.200.21.72\Data', and click finish.
*) Make sure the path to the conditions file is corrent

"""

import scipy.io
import numpy as np
import os
import time
import re
from glamsinterface.connect import db, db2
from ext.console import debug


def array2str(arr):
    arr=sorted(list(set(arr)))
    arr=[str(b) for b in arr]
    arr=','.join(arr)
    return arr

def getnConditions(dd):
    n=1
    n*=len(dd['orientations'].split(','))
    n*=len(dd['spatial_frequencies'].split(','))
    n*=len(dd['temporal_frequencies'].split(','))
    n*=len(dd['contrasts'].split(','))
    n*=len(dd['view_angles_horiz'].split(','))
    n*=len(dd['view_angles_horiz_offset'].split(','))
    if dd['blankOn']:
        n+=1
    return n

def meta2dict(m):
    d=dict()
    for i in range(len(m.dtype.names)):
        key=m.dtype.names[i]
        try:
            val=m[0][i][0]
        except IndexError:
            val=None
        if val=='?':
            val=None
        d[key]=val
    if d['weight'] is not None:
        d['weight']=float(re.sub("[^0-9.]", "",d['weight'])) #strips all non-numeric characters from string
    if 'e_name' in d and type(d['e_name']) is np.ndarray:
        d['e_name']=d['e_name'][0]
    return d

def files2db(c, c2):
    d=dict()
    if 'capfreq' in c2.keys():
        d['captureFrequency']       = c2['capfreq'][0][0] #float. frame rate (Hertz) of 2P data acquisition
    else:
        d['captureFrequency']       = 6.1 # 'capfreq' wasn't added to psychstim controller until beginning of 2013
    d['stimulus_type']          = c['StimulusStr'][c['StimulusNum'][0][0]-1][0][0] #string. The type of stimulus.  For example, "Drift Gratings" or  "Sweeping Noise"
    d['orientations']           = array2str(c['orient'][0]) #comma seperated string. Lists the different angles of orientations.
    d['spatial_frequencies']    = array2str(c['freq'][0]) #comma seperated string. Lists the spatial frequencies (cycles per degree) of visual stimulus.
    d['temporal_frequencies']   = array2str(c['TempFreq'][0]) #comma seperated string. Lists the temporal frequencies (Hz) of visual stimulus.
    d['contrasts']              = array2str(c['contrast'][0]) #comma seperated string. Lists the temporal frequencies (Hz) of visual stimulus.
    d['view_angles_horiz']      = array2str(c['length'][0]) #comma seperated string. Lists the width of the stimulus in degrees.  0 is full field.  20 is a 20 degree stimulus (when the monitor is set 25 cm from the eyes)
    d['view_angles_horiz_offset'] = array2str(c['positionX'][0]) #comma seperated string. offset of the view angle.  If set to 5, the stimulus is translated 5 degrees away from center.
    d['sequence']               = ','.join([str(b[0]) for b in c['condcount']]) #comma seperated string. The order of presentation of the different conditions.
    d['duration_S']             = c['Duration'][0][0] #float. How many seconds the stimulus is presented per orientation per repetition.
    d['duration_F']             = d['duration_S']*d['captureFrequency']
    d['waitInterval_S']         = c['WaitInterval'][0][0] #float. How many seconds between each stimulus presentation.
    d['waitInterval_F']         = d['waitInterval_S']*d['captureFrequency']
    d['condition_S']            = d['duration_S']+d['waitInterval_S']  # float. How long each condition lasts (in seconds).  duration_S+waitInterval_S
    d['condition_F']            = d['condition_S']*d['captureFrequency'] # float. How long each condition lasts (in frames).
    d['nReps']                  = int(c['nReps'][0]) #int. how many times each orientation was presented.
    d['blankOn']                = c['blankstim'][0][0] #boolean. Whether or not a blank stimulus was presented.
    d['nConditions']            = getnConditions(d) #How many conditions there are.
    d['ontimes_S']              = array2str(c['twoPhotonSyncData'][c['twoPhotonSyncData'][:,1]==1,:][:,2]) #comma seperated string. The on time (in seconds) of each stimulus.
    d['ontimes_F']              = array2str(c['twoPhotonSyncData'][c['twoPhotonSyncData'][:,1]==1,:][:,2] * d['captureFrequency'])
    d['total_time_S']           = c['twoPhotonSyncData'][-1,2]-c['twoPhotonSyncData'][0,2] #float. The total time of stimulus presentation in seconds.
    d['flickerOn']              = c['FullFlicker'][0][0]
    d['nPixelsX']               = c['PixelsX'][0][0] #float.  Number of pixels of the stimulus screen in the x direction.
    d['nPixelsY']               = c['PixelsY'][0][0] #float.  Number of pixels of the stimulus screen in the y direction.
    d['screenDist']             = c['ScreenDist'][0][0] #float.  Distance to screen from mouse's eyes in centimetres.
    d['monitorWidth']           = c['SizeX'][0][0] #Width of monitor in cm.
    d['monitorHeight']          = c['SizeY'][0][0] #Height of monitor in cm.

    metadata=meta2dict(c['meta_data'][0])
    d['animal_weight']          = metadata['weight']
    for k in d.keys():
        if type(d[k]) is np.float_:
            d[k]=float(d[k])
        if type(d[k]) is np.int_ or type(d[k]) is np.uint8 or type(d[k]) is np.uint16:
            d[k]=int(d[k])
        if type(d[k]) is np.unicode_:
            d[k]=str(d[k])

    return d

def add2db(dd):
    print('Mouse id = {}'.format(dd['mouse_id']))
    ans=db.execute("""
        SELECT mice.id FROM experiments
        LEFT JOIN mice ON mice.id=mouse_id
        LEFT JOIN lab_members ON experiments.lab_member_id=lab_members.id
        WHERE lab_members.id=%s
        AND experiments.date=%s
        AND mice.id=%s""",(dd['experimenter_id'], dd['date'],dd['mouse_id']))
    if ans==[]:
        print('No glams entry for animal on {}'.format(dd['date']))
        return 1
    if len(ans)>1:
        print("More than one experiment was done on this mouse today.  This is ambiguous.")
        return 1
    dd['mouse_id']=ans[0][0]
    db.config['database']='ed'
    ans2=db.execute("""SELECT mouse_id, experimenter_id, date, filename FROM 2P_visual_stims WHERE mouse_id=%s AND experimenter_id=%s AND date=%s AND filename=%s""",(dd['mouse_id'],dd['experimenter_id'], dd['date'],dd['filename']))
    if ans2!=[]: #if the entry is already in the database
        print('File {} from {} to database already exists.  File not added.'.format(dd['filename'],dd['date']))
        db.config['database']='glams'
        return 1
    print('this works')
    cols=''
    parameters=[]
    for key in dd.keys():
        cols+=" {}=%s,".format(key)
        parameters.append(dd[key])
    cols=cols[:-1]
    parameters=tuple(parameters)
    db.execute('INSERT INTO 2P_visual_stims SET {}'.format(cols),parameters)
    db.config['database']='glams'
    print('Added file {} from {} to database.'.format(dd['filename'],dd['date']))

def upload(experimenter_id,date,mouse_id,filename):
    experimenter=db.execute("SELECT name FROM lab_members WHERE id=%s",(experimenter_id,))[0][0]
    mouse_name=db.execute("SELECT name FROM mice WHERE id=%s",(mouse_id,))[0][0]
    currentdate=date.replace('-','.')
    print(currentdate)
    if os.environ['COMPUTERNAME']=='ARMSTRONG': # Kyle's computer
        pathTo2P='X:/Recordings/2P/'+experimenter+'/'+currentdate+'/'+mouse_name+'/'
        if os.path.isdir(pathTo2P) is False:
            pathTo2P='C:/Users/kyle/Desktop/recordings/'+experimenter+'/'+currentdate+'/'+mouse_name+'/'
        pathToCond='C:/Users/kyle/Dropbox/Data/Conditions/2P/'+time.strftime('%d-%b-%Y',time.strptime(currentdate,'%Y.%m.%d'))+'/'
    elif os.environ['COMPUTERNAME']=='MOM1':    # Aquisiton Computer
        pathTo2P='D:/data/'+experimenter+'/'+currentdate+'/'+mouse_name+'/'
        pathToCond='C:/Users/MOM1/Documents/Dropbox/Data/Conditions/2P/'+time.strftime('%d-%b-%Y',time.strptime(currentdate,'%Y.%m.%d'))+'/'
    if os.path.isdir(pathTo2P) is False:
        print('There is no directory {}'.format(pathTo2P))
        return False
    elif os.path.isdir(pathToCond) is False:
        print('There is no directory {}'.format(pathToCond))
        return False
    cond_files=os.listdir(pathToCond)
    print('pathToCond: {}'.format(pathToCond))
    for cond_file in cond_files:
        print('COND FILE: {}'.format(cond_file))
        base_name, ext = os.path.splitext(cond_file)
        print('pathTo2P: {}'.format((pathTo2P+base_name+'.tif')))
        if os.path.exists(pathTo2P+cond_file) and os.path.exists(pathTo2P+base_name+'.tif'):
            c=scipy.io.loadmat(pathToCond+cond_file)
            try:
                c2=scipy.io.loadmat(pathTo2P+cond_file)
                # debug.enter()
            except IOError:
                print("You need the 2P conditions file as well as the stimulus conditions file")
            if 'meta_data' in c.keys():
                dd=files2db(c,c2)
                dd['date']=time.strftime('%Y-%m-%d',time.strptime(currentdate,'%Y.%m.%d'))
                dd['filename']=base_name
                dd['experimenter_id']=experimenter_id
                dd['mouse_id']=mouse_id
                add2db(dd)
    print('All files uploaded to ED successfully')








