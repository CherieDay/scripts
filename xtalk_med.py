#! /usr/bin/env python

import numpy as np, aipy as a, sys

for uvfile in sys.argv[1:]:
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
	
	def med(uv, p, d, f): return p, d-med_data, f

	uv.rewind()
	uvo = a.miriad.UV(uvfile+'m',status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=med, raw=True,
		append2hist="Subtracted median for each frequency channel for cross-correlation (0,7)\n")

#	def medavg(uv, p, d, f):
#		uv.rewind()
#		d -= med_data
#		data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)
#		avg_data = np.mean(data.real, axis=0) + 1j*np.mean(data.imag, axis=0)
#		d -= avg_data
#		return p, d, f
