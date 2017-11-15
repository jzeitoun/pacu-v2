# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 12:00:23 2013
@author: kyle

google "python contours opencv" to find this opencv tutorial by abid rahman
Steps for cell counting.
1) Preprocess
  A) Background Subtraction- take a wide gaussian blur and subtract
  B) or Gaussian Blur
  C) or Median Filter
2) Threshold
  A) Pick a single threshold
  B) Pick multiple thresholds
3) Identify objects
4) Select objects by trait
5) Divide objects 
6) Print objects

"""
import cv2
from scipy.ndimage import gaussian_filter
from pylab import imshow
import numpy as np
#
#def test(i,j,thresh):
#    submat=gaussian_filter(mat,i)
#    tmp=mat-submat
#    pmat=gaussian_filter(tmp,j)
#    subplot(1,2,1)
#    imshow(pmat)
#    subplot(1,2,2)
#    imshow(pmat>thresh)

def preprocess(mat):
    submat=gaussian_filter(mat,6)
    tmp=mat-submat
    pmat=gaussian_filter(tmp,1)
    return pmat
    
def threshold(pmat):
    t=150
    tmat=pmat>t
    return tmat

def identify(tmat):
    tmat=255*tmat
    tmat=tmat.astype(np.uint8)
    ret, thresh=cv2.threshold(tmat,100,255,0) #thresh is an edge detected image
    contours, heirarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #contours contains, for every discrete blob, a list of [x,y] points around a cell
    return contours

def select(contours):
    #contours is a list
    #we can select only contours which meet particular requirements like roundness, size, etc.
    outlist=[]
    for h,cnt in enumerate(contours):
        area=cv2.contourArea(cnt)
        if area>10: # number of pixels 
            outlist.append(cnt)
    return outlist

def getintensity(outlist,mat):
    out=[]
    for cnt in outlist:
        mask=np.zeros(mat.shape,np.uint8)
        cv2.drawContours(mask,[cnt],0,255,1)
        mn=cv2.mean(mat,mask)
        out.append(mn[0])
    return out

def celldetect(mat):
    pmat=preprocess(mat)
    tmat=threshold(pmat)
    contours=identify(tmat)
    outlist=select(contours)
    return outlist


    
def outline(outlist,mat):
    for cnt in outlist:
        mask=np.zeros(mat.shape,np.uint8)
        cv2.drawContours(mask,[cnt],0,1,1)
        mat[mask==1]=mat.min()
    return mat

    
if __name__=="__main__":
    mat=cv2.imread("recording2.tif")
    mat=mat.mean(2)
    pmat=preprocess(mat)
    tmat=threshold(pmat)
    contours=identify(tmat)
    outlist=select(contours)
    out=getintensity(outlist,mat.astype(np.uint8))
