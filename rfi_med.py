#! /usr/bin/env python
from __future__ import division

import numpy as np, aipy as a, sys, optparse, matplotlib.pyplot as plt
from math import erf
from scipy.special import erfinv

for uvfile in sys.argv[1:]:
	print uvfile
	uv = a.miriad.UV(uvfile)
	uv.select('antennae', 0,7, include=True) # Include only the cross-correlation
	
	# Create a data array from a list built up of all the data from uvfile:
	data = np.array([d for p,d,f in uv.all(raw=True)], dtype=np.complex)

	# Get the variance for each frequency channel
	med_data = np.median(data.real, axis=0) + 1j*np.median(data.imag, axis=0)
	sig = np.sqrt(np.median(np.abs(data-med_data)**2, axis=0))

	# Determine outlier tolerance level using Chauvenet's criterion
		# nsig will be the number of sigma outside of which data will be flagged
	n = np.sqrt(2) * erfinv(1 - 0.5/len(data))
	nsig = n * sig

	def rfiflag(uv, p, d, f):
		absn = np.abs(d-med_data)
		nsig = n * np.median(absn)
		f = np.where(absn > nsig, 1, f)
		return p, np.where(f,0,d), f

	uv.rewind()
	uvo = a.miriad.UV(uvfile+'R', status='new')
	uvo.init_from_uv(uv)
	uvo.pipe(uv, mfunc=rfiflag, raw=True,
		append2hist='''Flagged values in data greater then nsig (determined using
		Chauvenet's criterion) for each frequency channel for cross-correlation (0,7)\n''')