import numpy as np

def make(t, x, y):
    dt = np.array([1.0, 1.25])
    dds = np.zeros_like(t)
    dts = np.zeros_like(t)
    dds[:] = np.nan
    dts[:] = np.nan
    done = False
    p1 = 0
    while not done:
        try:
            p2 = np.where(t[p1:] >= t[p1] + dt[0])[0][0] + p1;
        except:
            break
        if np.all(p2==0):
            done = True
        else:
            dds[p1] = np.sum(np.sqrt(np.diff(x[p1:p2+1])**2 + np.diff(y[p1:p2+1])**2))
            dts[p1] = t[p2] - t[p1]
            p1 += 1
    v = dds/dts
    # % Permit bin sizes between 1 to 1.25 times dt.
    v[np.isnan(dds)] = 0
    v[dts > dt[1]] = 0
    return v
