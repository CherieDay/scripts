#! /usr/bin/env python

from __future__ import division
import numpy as np, aipy as a, optparse, sys, matplotlib.pyplot as plt
from math import erf
from scipy.special import erfinv
from pylab import *

for uvfile in sys.argv[1:]:
    uv = a.miriad.UV(uvfile)
    uv.select('antennae', 0,7, include=True)

    data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

    med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)
    mean_data = np.mean(data.real, axis=0) + 1j*np.mean(data.imag, axis=0)

    sig_med = np.sqrt(np.median(np.abs(data-med_data)**2, axis=0))
    sig_mean = np.sqrt(np.var(data, axis=0, dtype=np.complex))

    n = np.sqrt(2.) * erfinv(1 - 0.5/len(data))

    data_med = np.where(np.abs(data)<=n*sig_med, data, 0)
    data_mean = np.where(np.abs(data)<=n*sig_mean, data, 0)

    med_newdata = np.median(data_med.real, axis=0) + 1j*np.median(data_med.imag, axis=0)
    mean_newdata = np.mean(data_mean.real, axis=0) + 1j*np.mean(data_mean.imag, axis=0)

    max_data = np.max(data, axis=0)
    max_data_med = np.max(data_med, axis=0)
    max_data_mean = np.max(data_mean, axis=0)

    print 'File: ', uvfile
#    print 'Median: ', med_data[380:390]
#    print 'Mean: ', mean_data[380:390]
#    print 'After flagging:'
#    print 'Median: ', med_newdata[380:390]
#    print 'Mean: ', mean_newdata[380:390]
    
    plt.plot(np.real(med_data), label='Median pre-flagging', linewidth=1.5)
    plt.plot(np.real(mean_data), label='Mean pre-flagging', linewidth=1.5)
    plt.plot(np.real(med_newdata), label='Median post-flagging', linestyle=':', linewidth=2.5)
    plt.plot(np.real(mean_newdata), label='Mean post-flagging', linestyle='-.', linewidth=3.5)
    plt.plot(np.real(med_data-med_newdata), label='Diff of pre- and post-flagged median', linestyle='--', linewidth=2.0)
    plt.plot(np.real(mean_data-mean_newdata), label='Diff of pre- and post-flagged mean', linestyle='--', linewidth=2.5)
    plt.plot(np.real(max_data), label='Max pre-flagged data')
    plt.plot(np.real(max_data_med), label='Max post-flagged with median data')
    plt.plot(np.real(max_data_mean), label='Max post-flagged with mean data', linestyle='-.', linewidth=2.0)

    legend(loc='upper left')
    plt.show()
