#! /usr/bin/env python

import numpy as np, aipy as a
import matplotlib.pyplot as plt
from pylab import *

#Directory path where all the test data resides
data_dir = '/Users/TheCreator/Documents/Research/data/paper_rx_tests/'

#Read in uv files for each test (cold temp with cal on and off; hot temp
#with cal on and off; room temp with cal on and off) and get the data
cold_cal_off_uv = a.miriad.UV(data_dir + '''cold_caloff_12:37.2457242.32771.uv''')
cold_cal_off_uv.select('antennae', 3,3, include=True)
cold_cal_off_data = np.array([d for p,d,f in cold_cal_off_uv.all(raw=True)])

cold_cal_on_uv = a.miriad.UV(data_dir + '''cold_calon_1:44.2457242.37423.uv''')
cold_cal_on_uv.select('antennae', 3,3, include=True)
cold_cal_on_data = np.array([d for p,d,f in cold_cal_on_uv.all(raw=True)])

hot_cal_off_uv = a.miriad.UV(data_dir + '''hot_caloff_3:19.2457242.43118.uv''')
hot_cal_off_uv.select('antennae', 3,3, include=True)
hot_cal_off_data = np.array([d for p,d,f in hot_cal_off_uv.all(raw=True)])

hot_cal_on_uv = a.miriad.UV(data_dir + '''hot_calon_3:16.2457242.42912.uv''')
hot_cal_on_uv.select('antennae', 3,3, include=True)
hot_cal_on_data = np.array([d for p,d,f in hot_cal_on_uv.all(raw=True)])

roomtemp_cal_off_uv = a.miriad.UV(data_dir + '''roomtemp_caloff_3:47.2457241.45968.uv''')
roomtemp_cal_off_uv.select('antennae', 3,3, include=True)
roomtemp_cal_off_data = np.array([d for p,d,f in roomtemp_cal_off_uv.all(raw=True)])

roomtemp_cal_on_uv = a.miriad.UV(data_dir + '''roomtemp_calon_3:12.2457241.43532.uv''')
roomtemp_cal_on_uv.select('antennae', 3,3, include=True)
roomtemp_cal_on_data = np.array([d for p,d,f in roomtemp_cal_on_uv.all(raw=True)])

#Get bandpass for each test: caloff/[calon-caloff]
bp_cold = np.mean((cold_cal_off_data / (cold_cal_on_data - cold_cal_off_data)), axis=0)
bp_hot = np.mean((hot_cal_off_data / (hot_cal_on_data - hot_cal_off_data)), axis=0)
bp_roomtemp = np.mean((roomtemp_cal_off_data / (roomtemp_cal_on_data - roomtemp_cal_off_data)), axis=0)

temp_diff = bp_hot - bp_cold
avg_temp_diff = np.mean(temp_diff[300:700])
tcal = 82.85 / np.real(avg_temp_diff) #Kelvin

bp_cold_caled = bp_cold*tcal - 274.3
bp_hot_caled = bp_hot*tcal - 357.15
bp_roomtemp_caled = bp_roomtemp*tcal - 262.45

freq = np.arange(100,200, step=100/1024., dtype=np.double) / 1000.
freqrange = freq[::-1]

print tcal

plt.plot(freqrange[90:755], bp_cold_caled[269:934], label='BP Cold', linestyle=':')
plt.plot(freqrange[90:755], bp_hot_caled[269:934], label='BP Hot', linestyle='-.')
plt.plot(freqrange[90:755], bp_roomtemp_caled[269:934], label='BP amb')
plt.xlabel('Frequency (GHz)')
plt.ylabel('Temperature (K)')

#plt.plot(freqrange, np.mean(np.abs(cold_cal_off_data), axis=0), label='Cold Cal Off')
#plt.plot(freqrange, np.mean(np.abs(cold_cal_on_data), axis=0), label='Cold Cal On')
#plt.ylabel('Power (arbitrary units)')
#plt.xlabel('Frequency (GHz)')


#plt.plot(freqrange, np.mean(np.abs(hot_cal_off_data), axis=0), label='Hot Cal Off')
#plt.plot(freqrange, np.mean(np.abs(hot_cal_on_data), axis=0), label='Hot Cal On')
#plt.plot(freqrange, np.mean(np.abs(roomtemp_cal_off_data), axis=0), label='Room temperature, Cal Off')
#plt.plot(freqrange, np.mean(np.abs(roomtemp_cal_on_data), axis=0), label='Room temperature, Cal On')
#plt.xlabel('Frequency (GHz)')
#plt.ylabel('Power (arbitrary units)')

plt.legend(loc='upper right')
plt.show()
