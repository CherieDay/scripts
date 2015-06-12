#! /usr/bin/env python

#Note: this program must be run on files that have already had the mean subtracted
#off since it assumes an offset of zero.

#Things to do:
#(1) Get variance (squared standard deviation) for each frequency channel over all the
#		times using numpy.var().
#(2) Once I have the variance, do a where value is larger then 6 sigma, add it to the
#		flags in the uv file.
#Note, since I am using the median subtracted files, the offset from zero is zero.
#How does file length (i.e. the length of time I'm finding the median over) affect 
#the standard deviation I calculate? Also, how many outliers would I expect to see
#at random given a Gaussian distribution?

import numpy as np, aipy as a, sys, optparse
from math import erf

o = optparse.OptionParser()
o.set_usage('rfi_flag.py [options] *.uv')
o.set_description(__doc__)
o.add_option('-m', '--mode', dest='mode', default='mean',
    help='Use either the standard definition of variance and standard deviation or use the root median squared deviation from the median to calculate the standard deviation for RFI flagging. e.g -m median. The mean is the default.')
#o.add_option('-n', '--nsigma', dest='nsigma', default='5',
#	help='The number of sigma desired for the tolerance level. That is, all values greater than nsigma will be flagged. e.g -n 5. 5 is the default.')

opts, args = o.parse_args(sys.argv[1:])

for uvfile in args:
	print uvfile
	uv = a.miriad.UV(uvfile)
	uv.select('antennae', 0,7, include=True) #Include only the cross-correlation
	
	#Create a data array from a list built up of all the data from uvfile:
	data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

	#Get the variance for each frequency channel
	sig_mean = np.sqrt(np.var(data, axis=0, dtype=np.complex))
	med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)
	med_abs = np.median(abs((data-med_data).real)**2, axis=0) + 1j*np.median(abs((data-med_data).imag)**2, axis=0)
	sig = np.sqrt(med_abs.real)+1j*np.sqrt(med_abs.imag)
	
	#Determine outlier tolerance level
		#nout is the number of data values outside i sigma
		#n will be the number of sigma outside of which data will be flagged
	i = 0
	while i < 7:
		nout = len(data)*(1-erf(i/np.sqrt(2.)))
		if nout<0.5:
			n = i
			break
		i+=0.1
	
	def rfiflag(uv, p, d, f):
		#n = float(opts.nsigma)
		if opts.mode == 'mean': return p, np.where(abs(d)<=n*sig_mean, d, 0.), np.where(abs(d)<n*sig_mean, f, True)
		elif opts.mode == 'median': return p, np.where(abs(d)<=n*sig, d, 0.), np.where(abs(d)<n*sig_med, f, True)
		else:  raise ValueError('Must specify either mean or median and/or nsigma.')

	uv.rewind()
	if opts.mode == 'mean':
		uvo = a.miriad.UV(uvfile+'R',status='new')
	elif opts.mode == 'median':
		uvo = a.miriad.UV(uvfile+'RM', status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=rfiflag, raw=True,
		append2hist='''Flagged values in data greater then nsigma for
		 each frequency channel for cross-correlation (0,7)\n''')



