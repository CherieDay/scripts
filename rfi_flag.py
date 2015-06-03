#! /usr/bin/env python

#Note: this program must be run on files that have already had the mean subtracted
#off since it assumes an offset of zero.

#Things to do:
#(1) Get variance (squared standard deviation) for each frequency channel over all the
#		times using numpy.var().
#(2) Once I have the variance, do a where value is larger then 6 sigma, add it to the
#		flags in the uv file.
#Note, since I am using the median subtracted files, the offset from zero is zero.

import numpy as np, aipy as a, sys

for uvfile in sys.argv[1:]:
	print uvfile
	uv = a.miriad.UV(uvfile)
	uv.select('antennae', 0,7, include=True) #Include only the cross-correlation
	
	#Create a data array from a list built up of all the data from uvfile:
	data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

	#Get the variance for each frequency channel
	dvar = np.var(data, axis=0, dtype=np.complex)
	
	def rfiflag(uv, p, d, f):
		f = np.where(abs(d)<6*dvar**(1/2), f, False)
		return p, d, f

	uv.rewind()
	uvo = a.miriad.UV(uvfile+'R',status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=rfiflag, raw=True,
		append2hist='''Flagged values in data greater then 6 sigma for
		 each frequency channel for cross-correlation (0,7)\n''')