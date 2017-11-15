from scipy import optimize

import numpy as np

def func(x, a, b, c, d):
    return a*np.exp(-c*(x-b))+d

def fit(y_meas):
    x = np.arange(len(y_meas))
    popt, _ = optimize.curve_fit(func, x, y_meas) #, [100,400,0.001,0])
    return popt[2], x, func(x, *popt)
