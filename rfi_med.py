#! /usr/bin/env python
from __future__ import division

import numpy as np, aipy as a, sys, optparse
from math import erf

for uvfile in sys.argv[1:]:
	print uvfile
	uv = a.miriad.UV(uvfile)
	uv.select('antennae', 0,7, include=True) #Include only the cross-correlation
	
	#Create a data array from a list built up of all the data from uvfile:
	data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

	#Get the variance for each frequency channel
	med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)
	med_abs = np.median(abs((data-med_data).real)**2, axis=0) + 1j*np.median(abs((data-med_data).imag)**2, axis=0)
	sig = np.sqrt(med_abs.real)+1j*np.sqrt(med_abs.imag)

	#Determine outlier tolerance level using Chauvenet's criterion
		#nout is the number of data values outside i sigma
		#n will be the number of sigma outside of which data will be flagged
	i = 0
	while i < 7:
		if len(data)*(1-erf(i/np.sqrt(2.)))<0.5:
			n = i
			break
		i+=0.1
	print n
#	print len(data)*(1-erf(n/np.sqrt(2.)))

	#Set flagged data values to zero using the median absolute deviation (MAD)
	for i in range(0,1023):
		absn = abs((data[:,i]-med_data[i]).real) + 1j*abs((data[:,i]-med_data[i]).imag)
		mad = np.median(absn.real) + 1j*np.median(absn.imag)
		data[:,i] = np.where((abs(absn/(1.4826*mad)))<=n, data[:,i], 0.)
#		data[:,i] = np.where((absn.imag/(1.4826*mad.imag))<=n, data[:,i], 0.)
		mad = np.where(abs(mad)!=0., mad, 1j)

	#Take the median of all the times in each frequency channel for real and imaginary
	#components of data
	new_med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)

	def rfiflag(uv, p, d, f):
		absn = abs((d-med_data).real) + 1j*abs((d-med_data).imag)
		mad = np.median(absn.real) + 1j*np.median(absn.imag)
		mad = np.where(abs(mad)!=0., mad, 1j)
		return p, np.where((abs(absn/(1.4826*mad)))<=n, d, 0.)-new_med_data, np.where((abs(absn/(1.4826*mad)))<n, f, True)

	uv.rewind()
	uvo = a.miriad.UV(uvfile+'RmM', status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=rfiflag, raw=True,
		append2hist='''Flagged values in data greater then nsigma (determined using
		Chauvenet's criterion for each frequency channel for cross-correlation (0,7)
		and then subtract median after RFI flagging\n''')


