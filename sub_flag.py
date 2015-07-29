#! /usr/bin/env python
from __future__ import division

import numpy as np, aipy as a, sys, optparse, matplotlib.pyplot as plt
from math import erf
from scipy.special import erfinv
import glob
import scipy.io.wavfile as wav

o = optparse.OptionParser()
o.set_usage('xtalk_med.py [options] *.uv')
o.set_description(__doc__)
o.add_option('-m', '--mode', dest='mode', default='median',
    help='Subtract either the median or the mean from the data. The default is the median. e.g. -m median or -m mean.')
o.add_option('-f', '--flag', dest='flag', action='store_true', help="RFI flag the data using all the files selected. This flagger uses Chauvenet's criterian to determine which data are flagged and set to zero.")

opts, args = o.parse_args(sys.argv[1:])

data_path = '/Users/TheCreator/Documents/Research/data/'
data_dir = input('Enter the data directory as a string: ')
data_files = sorted(glob.glob(data_path+data_dir+'/*.uv'))
numfiles = len(data_files)

uv = a.miriad.UV(data_files[0])
uv.select('antennae', 0,7, include=True)
data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

print 'Gathering data from ' + str(numfiles) +' files'

for uvfile in data_files[1:]:
    uv = a.miriad.UV(uvfile)
    uv.select('antennae', 0,7, include=True)

    newdata = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

    data = np.concatenate((data, newdata), axis=0)

if opts.mode == 'median':
    print 'Calculating median for each frequency channel'
    med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)
elif opts.mode == 'mean':
    print 'Calculating mean for each frequency channel'
    mean_data = np.mean(data.real, axis=0) + 1j*np.mean(data.imag, axis=0)

if opts.flag:
    print 'Preparing to flag...'
    if opts.mode == 'median':
        sig = np.sqrt(np.median(np.abs(data-med_data)**2, axis=0))
        n = np.sqrt(2.) * erfinv(1 - 0.5/len(data))
        nsig = n * sig

        for uvfile in data_files:
            print 'Processing: ' + uvfile[54:]
            uv = a.miriad.UV(uvfile)
            uv.select('antennae', 0,7, include=True)

            def rfiflagsub(uv, p, d, f):
                absn = np.abs(d-med_data)
                f = np.where(absn > nsig, 1, f)
                return p, np.where(f,0,d)-med_data, f

            uv.rewind()
            uvo = a.miriad.UV(uvfile+'Rm', status='new')
            uvo.init_from_uv(uv)
            uvo.pipe(uv, mfunc=rfiflagsub, raw=True, append2hist="Flags data using Chauvenet's criterion and subtracts the median obtained for " + str(numfiles) + " files for each frequency channel for the cross-correlation (0,7).\n")

    if opts.mode == 'mean':
        sig = np.sqrt(np.var(data, axis=0, dtype=np.complex))
        n = np.sqrt(2.) * erfinv(1 - 0.5/len(data))
        nsig = n * sig

        for uvfile in data_files:
            print 'Processing: ' + uvfile[54:]
            uv = a.miriad.UV(uvfile)
            uv.select('antennae', 0,7, include=True)

            def rfiflagsub(uv, p, d, f):
                absn = np.abs(d-mean_data)
                f = np.where(absn > nsig, 1, f)
                return p, np.where(f,0,d)-mean_data, f

            uv.rewind()
            uvo = a.miriad.UV(uvfile+'Rme', status='new')
            uvo.init_from_uv(uv)
            uvo.pipe(uv, mfunc=rfiflagsub, raw=True, append2hist="Flags data using Chauvenet's criterion and subtracts the mean obtained for " + str(numfiles) +" files for each frequency channel for the cross-correlation (0,7).\n")

if not opts.flag:
    for uvfile in data_files:
        print 'Processing: ' + uvfile[54:]
        uv = a.miriad.UV(uvfile)
        uv.select('antennae', 0,7, include=True)

        def medsub(uv, p, d, f):
            if opts.mode == 'median': return p, d-med_data, f
            if opts.mode == 'mean': return p, d-mean_data, f

        uv.rewind()
        if opts.mode == 'median':
            uvo = a.miriad.UV(uvfile+'m', status='new')
        elif opts.mode == 'mean':
            uvo = a.miriad.UV(uvfile+'me', status='new')
        uvo.init_from_uv(uv)
        uvo.pipe(uv, mfunc=medsub, raw=True, append2hist="Subtracts median or mean obtained for " +str(numfiles)+" files for each frequency channel for cross-correlation (0,7)\n")


#phs = np.angle(data)
#scaleddata = -32768.0 + 65535.0*(phs-np.amin(phs,axis=0))/(np.amax(phs,axis=0)-np.amin(phs,axis=0))
#plt.plot(scaleddata[:,380])
#plt.show()
#wav.write('audification.wav', 44100, scaleddata[:,380])
