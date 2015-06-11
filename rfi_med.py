#! /usr/bin/env python

import numpy as np, aipy as a, sys, optparse
from math import erf

o = optparse.OptionParser()
o.set_usage('rfi_flag.py [options] *.uv')
o.set_description(__doc__)
#o.add_option('-m', '--mode', dest='mode', default='median',
#    help='Use the root median squared deviation from the median to calculate the standard deviation for RFI flagging. e.g -m median.')

opts, args = o.parse_args(sys.argv[1:])

for uvfile in args:
	print uvfile
	uv = a.miriad.UV(uvfile)
	uv.select('antennae', 0,7, include=True) #Include only the cross-correlation
	
	#Create a data array from a list built up of all the data from uvfile:
	data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

	#Get the variance for each frequency channel
	sig_med = np.sqrt(np.median((abs(data-np.median(data,axis=0)))**2,axis=0))
	
	#Determine outlier tolerance level using Chauvenet's criterion
		#nout is the number of data values outside i sigma
		#n will be the number of sigma outside of which data will be flagged
	i = 0
	while i < 7:
		if len(data)*(1-erf(i/np.sqrt(2.)))<0.5:
			n = i
			break
		i+=0.1

	#Set flagged data values to zero
	data = np.where(abs(data)<=n*sig_med, data, 0.)
	
	#Take the median of all the times in each frequency channel for real and imaginary
	#components of data
	med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)

	def rfiflag(uv, p, d, f):
		return p, np.where(abs(d)<=n*sig_med, d, 0.)-med_data, np.where(abs(d)<n*sig_med, f, True)

	uv.rewind()
	uvo = a.miriad.UV(uvfile+'RmM', status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=rfiflag, raw=True,
		append2hist='''Flagged values in data greater then nsigma (determined using
		Chauvenet's criterion for each frequency channel for cross-correlation (0,7)
		and then subtract median after RFI flagging\n''')


