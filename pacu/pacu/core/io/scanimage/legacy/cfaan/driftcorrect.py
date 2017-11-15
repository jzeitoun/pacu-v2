# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 16:40:19 2013

@author: kyle
"""
from __future__ import division # Enable the new behaviour
import numpy as np
import cv2

def smoothMotion(motionVectors,polyorder=2):
    '''Polynomial smoothing of motionVectors'''
    v0=[i[0] for i in motionVectors]
    x=np.arange(len(v0))
    z=np.polyfit(x,v0,polyorder)
    p=np.poly1d(z)
    v0=p(x)
    v1=[i[1] for i in motionVectors]
    x=np.arange(len(v1))
    z=np.polyfit(x,v1,polyorder)
    p=np.poly1d(z)
    v1=p(x)
    motionVectors2=np.array([np.array([v0[i],v1[i]]) for i in np.arange(len(v0))])
    return motionVectors2

def getdrift1(green,sample_interval=400):
    ''' This method is based on computing the optical flow between average frames.
    The drift between two average frames is the average of the optical flow in a window of the frames'''
    motionVectors=[[0,0]]
    i=np.arange(sample_interval)
    i+=sample_interval
    prev=green[0:sample_interval].mean(0)
    while(i[-1]<green.shape[0]-1):
        next=green[i].mean(0)
        flow = cv2.calcOpticalFlowFarneback(prev,next, 0.5,1,3,15,3,5,1)
        motionVectors.append([flow[20:-20,20:-20,0].mean(),flow[20:-20,20:-20,1].mean()])
        prev=next
        i+=sample_interval
        #imshow(flow[20:-20,20:-20,0])
        #imshow(prev)
    next=green[i[0]:].mean(0)
    flow = cv2.calcOpticalFlowFarneback(prev,next, 0.5,1,3,15,3,5,1)
    motionVectors.append([flow[:,:,0].mean(),flow[:,:,1].mean()])
    motionVectors=np.array(motionVectors)
    for i in np.arange(motionVectors.shape[0]-1)+1:
        motionVectors[i]=motionVectors[i]+motionVectors[i-1] #take the integral, so we have position rather than velocity
    motionVectors=np.repeat(motionVectors,sample_interval,axis=0)
    return motionVectors

def getdrift2(green,sample_interval=100):
    ''' This works by creating a list of frames averaged by every sample_interval.
    This is a more robust solution than getdrift1'''
    frames=[]
    nframes=int(np.ceil(green.shape[0]/sample_interval)+1)
    #create the list of frames
    for n in np.arange(nframes):
        f=green[n*sample_interval:(n+1)*sample_interval].mean(0)
        frames.append((f*256/green.max()).astype('uint8'))
    allvectors=[]
    
    for i in range(nframes-1):
        motionVectors=[]
        for j in range(nframes-1):
            flow = cv2.estimateRigidTransform(frames[i],frames[j],False)
            motionVectors.append([flow[0,2],flow[1,2]])
        motionVectors=np.array(motionVectors)
        allvectors.append(motionVectors)
        
    # take the derivative so all the vectors look similar
    allvectors_d=[]
    for v in allvectors:
        motionVectors_d=[np.array([0,0])]
        for f in np.arange(nframes-2)+1:
            motionVectors_d.append(v[f]-v[f-1])
        motionVectors_d=np.array(motionVectors_d)
        allvectors_d.append(motionVectors_d)
    allvectors_d=np.array(allvectors_d)
    motionVectors=np.median(allvectors_d,0)
    
    # take the integral so we have position rather than velocity
    for i in np.arange(motionVectors.shape[0]-1)+1:
        motionVectors[i]=motionVectors[i]+motionVectors[i-1] #take the integral, so we have position rather than velocity
    motionVectors=np.repeat(motionVectors,sample_interval,axis=0)
    motionVectors2=smoothMotion(motionVectors,3)     #fit with polynomial
    return motionVectors2
    

def getdrift3(green,sample_interval=100):
    ''' This works the same as getdrift2 except it applies a canny edge detection before
    estimating the rigid transform.'''
    frames=[]
    nframes=int(np.ceil(green.shape[0]/sample_interval))+1
    print '\t* create the list of frames'
    for n in np.arange(nframes):
        if green[n*sample_interval:(n+1)*sample_interval].shape[0]>0:
            f=green[n*sample_interval:(n+1)*sample_interval].mean(0)
            f=(f*256/green.max()).astype('uint8')
        frames.append(f)
    allvectors=[]
    print '\t* apply adaptive threshold'
    for n in np.arange(nframes):
        frames[n]=cv2.adaptiveThreshold(frames[n],255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11,0)
        #frames[n]=cv2.Canny(frames[n],20,60)

    print '\t* collect vectors'
    for i in range(nframes-1):
        motionVectors=[]
        for j in range(nframes-1):
            flow = cv2.estimateRigidTransform(frames[i],frames[j],False)
            if flow is None: #sometimes cv2.estimateRigidTransform returns None.  If that happens, just use the previous value or [0,0]
                if motionVectors != []: 
                    motionVectors.append(motionVectors[-1])
                else:
                    motionVectors.append([0,0])
            else:
                motionVectors.append([flow[0,2],flow[1,2]])
        motionVectors=np.array(motionVectors)
        allvectors.append(motionVectors)

    print '\t* take the derivative so all the vectors look similar'
    allvectors_d=[]
    for v in allvectors:
        motionVectors_d=[np.array([0,0])]
        for f in np.arange(nframes-2)+1:
            motionVectors_d.append(v[f]-v[f-1])
        motionVectors_d=np.array(motionVectors_d)
        allvectors_d.append(motionVectors_d)
    allvectors_d=np.array(allvectors_d)
    motionVectors=np.median(allvectors_d,0)

    print '\t* take the integral so we have position rather than velocity'
    for i in np.arange(motionVectors.shape[0]-1)+1:
        motionVectors[i]=motionVectors[i]+motionVectors[i-1] #take the integral, so we have position rather than velocity
    motionVectors=np.repeat(motionVectors,sample_interval,axis=0)

    motionVectors2=smoothMotion(motionVectors,3)     #fit with polynomial
    return motionVectors2



def driftcorrect(green,motionVectors):
    ''' motionVectors[n][0] is the change in x position between frames n-1 and n
    motionVectors[n][1] is the change in y position between frames n-1 and n'''
    motionVectors=motionVectors.round()
    x=motionVectors[:,0].astype('int')
    y=motionVectors[:,1].astype('int')
    x=x.max()-x
    y=y.max()-y
    (mt,my,mx,mc)=np.shape(green) #mc is the number of color channels
    newgreen=np.zeros([mt,my+y.max(),mx+x.max(),mc])
    for t in np.arange(mt):
        newgreen[t,y[t]:my+y[t],x[t]:mx+x[t],:]=green[t,:,:,:]
    return newgreen

def driftcorrect2(green,motionVectors):
    ''' motionVectors[n][0] is the change in x position between frames n-1 and n
    motionVectors[n][1] is the change in y position between frames n-1 and n'''
    motionVectors=motionVectors.round()
    x=motionVectors[:,0].astype('int')
    y=motionVectors[:,1].astype('int')
    x=x.max()-x
    y=y.max()-y
    (mt,my,mx)=np.shape(green) #mc is the number of color channels
    newgreen=np.zeros([mt,my+y.max(),mx+x.max()], dtype='uint16')
    for t in np.arange(mt):
        newgreen[t, y[t]:my+y[t], x[t]:mx+x[t]]=green[t,:,:]
    return newgreen
