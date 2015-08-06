#! /usr/bin/env python

from __future__ import division
import numpy as np, aipy as a, optparse, sys, matplotlib.pyplot as plt
from math import erf
from scipy.special import erfinv
from pylab import *
import glob

data_path = '/Users/TheCreator/Documents/Research/data/'
data_dir = input('Enter the data directory as a string: ')
data_files = sorted(glob.glob(data_path+data_dir+'/*.uv'))
numfiles = len(data_files)

uv = a.miriad.UV(data_files[0])
uv.select('antennae', 0,7, include=True)
data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

print 'Gathering data from ' + str(numfiles) + ' files'

for uvfile in data_files[1:]:
    print uvfile
    uv = a.miriad.UV(uvfile)
    uv.select('antennae', 0,7, include=True)

    newdata = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)
    data = np.concatenate((data, newdata), axis=0)

print 'Calculating median per frequency channel on all data'
med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)

print 'Calculating mean per frequency channel on all data'
mean_data = np.mean(data.real, axis=0) + 1j*np.mean(data.imag, axis=0)

print 'Calculating standard deviation from median'
sig_med = np.sqrt(np.median(np.abs(data-med_data)**2, axis=0))

print 'Calculating standard deviation from mean'
sig_mean = np.sqrt(np.var(data, axis=0, dtype=np.complex))

print 'Calculating the number of sigma outside of which data will be flagged'
n = np.sqrt(2.) * erfinv(1 - 0.5/len(data))

print 'Flagging data using median sigma'
data_med = np.where(np.abs(data)<=n*sig_med, data, 0)

print 'Flagging data using mean sigma'
data_mean = np.where(np.abs(data)<=n*sig_mean, data, 0)

print 'Calculating post-flagging median'
med_newdata = np.median(data_med.real, axis=0) + 1j*np.median(data_med.imag, axis=0)

print 'Calculating post-flagging mean'
mean_newdata = np.mean(data_mean.real, axis=0) + 1j*np.mean(data_mean.imag, axis=0)

print 'Calculating maximum of raw data'
max_data = np.max(data, axis=0)

print 'Calculating maximum of median flagged data'
max_data_med = np.max(data_med, axis=0)

print 'Calculating maximum of mean flagged data'
max_data_mean = np.max(data_mean, axis=0)

print 'Plotting...'

plt.plot(np.real(med_data), label='Median pre-flagging', linewidth=1.5)
plt.plot(np.real(med_newdata), label='Median post-flagging', linestyle=':', linewidth=2.5)
legend(loc='upper left')
plt.show()

plt.plot(np.real(mean_data), label='Mean pre-flagging', linewidth=1.5)
plt.plot(np.real(mean_newdata), label='Mean post-flagging', linestyle='-.', linewidth=3.5)
legend(loc='upper left')
plt.show()

plt.plot(np.real(med_data-med_newdata), label='Diff of pre- and post-flagged median', linestyle='-', linewidth=2.0, color='c')
plt.plot(np.real(mean_data-mean_newdata), label='Diff of pre- and post-flagged mean', linestyle=':',linewidth=2.5, color='m')
legend(loc='lower left')
plt.show()

plt.plot(np.real(max_data), label='Max pre-flagged data', linestyle='-', linewidth=2.0, color='Khaki')
plt.plot(np.real(max_data_med), label='Max post-flagged with median data', linewidth=2.0, linestyle='--',  color='c')
plt.plot(np.real(max_data_mean), label='Max post-flagged with mean data', linestyle='-.', linewidth=2.0, color='m')
legend(loc='lower left')
plt.show()
