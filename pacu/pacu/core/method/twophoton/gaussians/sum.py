# -*- coding: utf-8 -*-

from scipy.optimize import brute
from scipy.optimize import leastsq

from numpy import exp
import numpy as np
from scipy.interpolate import interp1d
# from ext.console import debug

np.set_printoptions(suppress=True) #turn off scientific notation

def get_sumofgaussians(x,p):
    global prefs
    A_1, A_2, sigma, offset=p
    if sigma>0:
        sumofgaussians= A_1*exp(-((x-prefs[0])/sigma)**2)+\
                        A_1*exp(-((x-prefs[1])/sigma)**2)+\
                        A_2*exp(-((x-prefs[2])/sigma)**2)+\
                        A_2*exp(-((x-prefs[3])/sigma)**2)+\
                        offset
    else:
        sumofgaussians=np.ones(x.shape)*offset

    return sumofgaussians

def get_residuals_brute(p,y_meas_stretch,x_stretch):
    err = y_meas_stretch-get_sumofgaussians(x_stretch,p)
    err=sum(err**2)
    return err

def curve_fit_brute(y_meas_stretch,x_fit):
    #[A_1, A_2, sigma, offset]
    #DXFV notices a bad fit when average dF/d0 values are high (e.g. 5)...can fix by setting A1 and A2 to (0,10) - 2015.09.03
    ranges=((0,1),(0,1),(15,60),((0,.01)))
    p_fit,residual,grid,Jout=brute(get_residuals_brute, ranges, args=(y_meas_stretch,x_fit),Ns=5,full_output=True,finish=None)
    #print('p_fit = {}'.format(p_fit))
    #print('residual = {}'.format(residual))
    return p_fit

    # I tried zooming in with brute force but it didn't work
    #    limits=((0,10),(0,10),(0,60),(0,10))
    #    p_fit=[5,5,30,5]
    #    lengths=np.array([5,5,30,5])
    #    ranges=np.array([np.array([p_fit[i]-lengths[i],p_fit[i]+lengths[i]]) for i in range(len(p_fit))])
    #    for n in range(15):
    #        print(ranges)
    #        ranges=tuple(tuple(r) for r in ranges)
    #        p_fit,residual,grid,Jout=brute(get_residuals_brute, ranges, args=(y_meas_stretch,x_stretch),Ns=5,full_output=True,finish=None)
    #        lengths/=2
    #        ranges=np.array([np.array([p_fit[i]-lengths[i],p_fit[i]+lengths[i]]) for i in range(len(p_fit))])
    #        for i in range(len(ranges)):
    #            if ranges[i][0]<limits[i][0]:
    #                ranges[i]-=ranges[i][0]
    #            elif ranges[i][1]>limits[i][1]:
    #                ranges[i]-=(ranges[i][1]-limits[i][1])


def within_bounds(p):
    A_1, A_2, sigma, offset=p
    if A_1<0 or A_2<0:
        return False     
    elif sigma>90 or sigma<15: # sigma>15 constraint in Chen et. al. 2013, about GCaMP6
        return False
    elif offset<0:
        return False
    else:
        return True

def get_residuals_leastsq(p,y,x):
    if not within_bounds(p):
        return 1e12
    err = y-get_sumofgaussians(x,p)
    return err

def stretch(x,y):
    x=np.append(x,360)
    y=np.append(y,y[0])
    f=interp1d(x,y)
    x_new=np.arange(0,360,1)
    return x_new, f(x_new)

def curve_fit_leastsq(p,y_meas_stretch,x_fit):
    leastsq_ans=leastsq(get_residuals_leastsq,p,args=(y_meas_stretch,x_fit), ftol=.001, maxfev=100, full_output=True, diag=(1,1,100,1) )
    p_fit=leastsq_ans[0]
    #print('p_fit = {}'.format(p_fit))
    return p_fit

def get_preferred_orientation(x,y):
    #Niell and Stryker 2008
    x_rad=np.deg2rad(x) #convert x to radians
    numerator=sum(y*np.exp(2j*x_rad))
    denomenator=sum(y)
    oPref=np.angle(numerator/denomenator,deg=True)
    if oPref<0:
        oPref+=360
    oPref=oPref/2
    return oPref

def fit(x, y_meas):
    global prefs
    x=np.array(x)
    y_meas=np.array(y_meas)
    oPref=get_preferred_orientation(x,y_meas) # it will always fall between 0 and 180
    #print('preferred fit: {}'.format(oPref))
    oOppos=oPref+180
    oPref2=oPref+360
    oOppos2=oPref-180
    prefs=[oPref,oPref2,oOppos,oOppos2]
    #[A_1, A_2, sigma, offset]
    #p0=[1,.1,15,.10] # these are the starting conditions
    x_fit, y_meas_stretch=stretch(x,y_meas)#DXFV - change to np.absolute(stretch(x,y_meas)) when trace flipped sign

    # SPG 14JAN2016: appears to be a legacy code
    p_fit = curve_fit_brute(y_meas_stretch,x_fit)
    #print(p_fit)
    #p_fit=[.1,.2,20,0]
    p_fit = curve_fit_leastsq(p_fit,y_meas_stretch,x_fit)
    #print(p_fit)

    if p_fit[0]>p_fit[1]:
        o1=oPref
        o2=oOppos
    else:
        o2=oPref
        o1=oOppos
    oPref=o1
    oOppos=o2

    y_fit=get_sumofgaussians(x_fit,p_fit)
    residuals=get_residuals_leastsq(p_fit,y_meas_stretch,x_fit)
    residual=sum(residuals**2)
    return (p_fit, residual, [x_fit, y_fit],[oPref, oOppos])
#
#
#    leastsq_ans=leastsq(get_residuals,p0,args=(y_meas_stretch,x_stretch), ftol=.0001, maxfev=10000, full_output=True, diag=(1,1,100,1) )
#    p_fit=leastsq_ans[0]
#    #print(leastsq_ans[3])
#    residuals=get_residuals(p_fit,y_meas,x)
#    residual=sum(residuals**2)
#    x=np.linspace(0,360,200)
#    y_fit=get_sumofgaussians(x,p_fit)
#    p_fit=list(p_fit)
#    p_fit.append(oPref)
#    p_fit.append(oOppos)
#    return ([x,y_fit],residual, p_fit)

if __name__=='__main__':
    from matplotlib import pyplot as plt
    y_meas=[0.078989953,	0.062350908,	0.054497087,	0.0660818,	0.085982476,	0.071674218,	0.069031322,	0.044009004,	0.021679617,	0.085038428,	0.033340394,	0.011727786]
    y_meas=[0.070116071,	0.004194811,	0.027585504,	0.017245428,	0.021334857,	0.102061843,	0.053934116,	0.028131623,	0.020282417,	0.026957683,	0.000977683,	0.031002123]

    x=np.array([   0.,   30.,   60.,   90.,  120.,  150.,  180.,  210.,  240., 270.,  300.,  330.])
    p_fit, residual, [x_fit,y_fit], omax=fit(x,y_meas)
    print('residual={}'.format(residual))
    plt.plot(x,y_meas,'o')
    plt.plot(x_fit,y_fit)


    theta_pref, theta_oppos = omax
    theta_ortho=(theta_pref+theta_oppos)/2
    x=np.array([theta_pref,theta_ortho])
    R_pref,R_ortho=get_sumofgaussians(x,p_fit)
    OSI=(R_pref-R_ortho)/(R_pref+R_ortho)
    print('OSI = {}'.format(OSI))





