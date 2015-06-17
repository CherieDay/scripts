#! /usr/bin/env python

import numpy as np, aipy as a, sys, optparse

o = optparse.OptionParser()
o.set_usage('xtalk_med.py [options] *.uv')
o.set_description(__doc__)
o.add_option('-m', '--mode', dest='mode', default='median',
    help='Subtract either the median or the mean from the data. The default is the median. e.g. -m median or -m mean.')

opts, args = o.parse_args(sys.argv[1:])

for uvfile in args:
	print uvfile
	uv = a.miriad.UV(uvfile)
	uv.select('antennae', 0, 7, include=True)  #This tells it I want to include only the cross-correlations

	#For the following uv.all(raw=True) (Reads all info from uv file) call:
		#uvw is the baseline info--which we don't know, so it's useless right now--->update this when we do know
		#t is the Julian day
		#(i,j) are the antenna polarizations we want to use--here we used 0,7
		#d is the actual data--the spectrum--the uv file contains many spectra
		#f are the flags--if any of the data are flagged as bad (1) or good (0)

	data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

	#Take the median of all the times in each frequency channel for real and imaginary
	#components of data
	med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)
	mean_data = np.mean(data.real, axis=0) + 1j*np.mean(data.imag, axis=0)
	
	def med(uv, p, d, f):
		if opts.mode == 'median': return p, d-med_data, f
		elif opts.mode == 'mean': return p, d-mean_data, f

	uv.rewind()
	if opts.mode == 'median':
		uvo = a.miriad.UV(uvfile+'m',status='new')
	elif opts.mode == 'mean':
		uvo = a.miriad.UV(uvfile+'me',status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=med, raw=True,
		append2hist="Subtracted median for each frequency channel for cross-correlation (0,7)\n")