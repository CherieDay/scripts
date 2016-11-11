#! /usr/bin/env python

#Plot of spiral antenna r, theta for use as a guide in placing the wire.

#Science Band: 50-100MHz
#lambda_50 = 599.6cm
#lambda_100 = 299.8cm
#One wavelength =  circumference of the spiral. 2*pi*r = lambda

#For the equation: r = r_0 + a*phi (for a Archimedean spiral antenna)
# r is the final radius
# r_0 is the initial radius (here the distance from the transformer 
#    pin or SMA connector to the center of the first turn
# a = 2w/pi; parameter that controls the rate at which the spiral
#    flares out
# w is the width of the wire (or plate)
# s is the width of the air slot between the wire (or plate); in a
#    self-complkimentary antenna, w=s
# phi is angle in which r grows
# n is the number of full turns to make; 2*pi*n = phi

import numpy as np, matplotlib.pyplot as plt
from pylab import *

r_0 = 2.*0.466 #0.466 #cm; using w=5mm; make flush with inner edge of balun pin
#r_0 = 0.254 #cm; for transformer connection seperation
#r_0 = (0.67*2.54)/2. #cm; for sma connector seperation; note that the center
             #is at zero, such that one arm starts at r_0 and the
             #other at -r_0
#r2 = 15.24 #cm; center to tip of spiral (for 12in x 12in antenna)
r2 = 269.9 #cm; center to tip of spiral (for science band antenna)

#w = 0.102 #cm; diameter of 18 gauge wire
w = 1.0#0.5 #cm
a = (4.*w)/(2.*np.pi) #cm; 
#4w=0.8cm is the distance out to one full turn for w=0.2cm
pin_width = 0.076 #cm; width of each pin on the balun

n = (r2-r_0)/(a*2.*np.pi) #number of turns to get to r2

r_1st_arm = np.linspace(r_0+w/2., r2+w/2., 1e5)
r_1st_arm_2 =  np.linspace(r_0-w/2., r2-w/2., 1e5)

r_2nd_arm = np.linspace(-r_0+w/2., -r2+w/2., 1e5)
r_2nd_arm_2 = np.linspace(-r_0-w/2., -r2-w/2., 1e5)

phi = np.linspace(0, 2.*np.pi*n, 1e5) #for opposite polarization: make
                                      #middle term negative
phi_piov2 = np.where(phi > np.pi/2.)
phi_piov4 = np.where(phi > np.pi/4.)

#Define the Cartesian arrays of each arm to be plotted; note each
#defined x and y of an arm defines the edges of the two arms
#First arm:
x,y = r_1st_arm*np.cos(phi), r_1st_arm*np.sin(phi) #cm
x1,y1 = r_1st_arm_2*np.cos(phi), r_1st_arm_2*np.sin(phi) #cm
#Second arm:
x2, y2 = r_2nd_arm*np.cos(phi), r_2nd_arm*np.sin(phi) #cm
x2_2, y2_2 = r_2nd_arm_2*np.cos(phi), r_2nd_arm_2*np.sin(phi) #cm

#Tapered arm piece for 1st arm:
#Following the quadratic equation z=a*h^2 + b*h + c:
z, h = r_0-w/2.+pin_width/2., 0.0
z1, h1 = x[phi_piov2][0], y[phi_piov2][0]
z2, h2 = x[phi_piov4][0], y[phi_piov4][0]#2*0.09, 2*1.17

c = z
a = (1/(1-(h2/h1)))*( ((z1-c)/h1**2.) - ((z2-c)/(h1*h2)) )
b = (1/(1-(h2/h1)))*( ((z2-c)/h2) - (h2*(z1-c)/(h1**2)) )

quad_y_1 = np.linspace(0, y[phi_piov2][0], 1e5)
quad_x_1 = a*quad_y_1**2 + b*quad_y_1 + c

#Tapered arm peice for 2nd arm; follows q = d*k^2 + f*k + g
q, k = -r_0+w/2.-pin_width/2., 0.0
q1, k1 = x2_2[phi_piov2][0], y2_2[phi_piov2][0]
q2, k2 = x2_2[phi_piov4][0], y2_2[phi_piov4][0]#-2*0.09, -2*1.17

g = q
d = (1/(1-(k2/k1)))*( ((q1-g)/k1**2.) - ((q2-g)/(k1*k2)) )
f = (1/(1-(k2/k1)))*( ((q2-g)/k2) - (k2*(q1-g)/(k1**2)) )

quad_y_2 = np.linspace(0, y2_2[phi_piov2][0], 1e5)
quad_x_2 = d*quad_y_2**2 + f*quad_y_2 + g

#Square ending to taper--cuts off so the two arms can be placed directly
#on the balun board
sq_x_1, sq_y_1 = quad_x_1[0], quad_y_1[0]
sq_x_2, sq_y_2 = x2[15], y2[15]#0.05, 0 #x2[0], y2[0]
sq_line_x_1 = np.linspace(sq_x_1, sq_x_2, 1e5)
sq_line_y_1 = np.linspace(sq_y_1, sq_y_2, 1e5)

sq_x_3, sq_y_3 = quad_x_2[0], quad_y_2[0]
sq_x_4, sq_y_4 = x1[15], y1[15]#-0.05, 0 #quad_x_2[3.5e4], quad_y_2[3.5e4]
sq_line_x_2 = np.linspace(sq_x_3, sq_x_4, 1e5)
sq_line_y_2 = np.linspace(sq_y_3, sq_y_4, 1e5)

#Pieces of original curve to remove--tests
cutbit_x_1, cutbit_y_1 = quad_x_1[0:3.5e4], quad_y_1[0:3.5e4]
cutbit_x_2, cutbit_y_2 = quad_x_2[0:3.5e4], quad_y_2[0:3.5e4]
cutbit_x_3, cutbit_y_3 = x1[0:148], y1[0:148]
cutbit_x_4, cutbit_y_4 = x2[0:148], y2[0:148]

plt.xlim(-5,5)
plt.ylim(-5,5)

plt.plot(x[phi_piov4], y[phi_piov4], color='b')
plt.plot(x1[15:],y1[15:], color='b')

plt.plot(x2[15:],y2[15:], color='g')
plt.plot(x2_2[phi_piov4], y2_2[phi_piov4], color='g')

plt.plot(quad_x_1[0:5.6194e4], quad_y_1[0:5.6194e4], color='b')
plt.plot(quad_x_2[0:5.6194e4], quad_y_2[0:5.6194e4], color='g')

plt.plot(sq_line_x_1, sq_line_y_1, color='r')
plt.plot(sq_line_x_2, sq_line_y_2, color='r')

#plt.plot(cutbit_x_1, cutbit_y_1, color='black')
#plt.plot(cutbit_x_2, cutbit_y_2, color='black')
#plt.plot(cutbit_x_3, cutbit_y_3, color='black')
#plt.plot(cutbit_x_4, cutbit_y_4, color='black')

plt.show()

#dim = (2.6*max(x))/2.54

dim = 12./2.54 #dimension for test print to determine if balun will fit

fig = plt.figure(figsize=(dim, dim))

ax1 = fig.add_subplot(1, 1, 1)
ax1.set_aspect('equal', 'datalim')
ax2 = ax1.twinx()
ax2.set_aspect('equal', 'datalim')
ax3 = ax1.twiny()
ax3.set_aspect('equal', 'datalim')

#circle1 = plt.Circle((0,0), r1, fill=False, color='b')
#plt.gcf().gca().add_artist(circle1)

ax1.plot(x[phi_piov4], y[phi_piov4], linewidth=0.1, color='blue')
ax1.plot(x1[15:], y1[15:], linewidth=0.1, color='blue')
ax1.plot(x2[15:], y2[15:], linewidth=0.1, color='green')
ax1.plot(x2_2[phi_piov4], y2_2[phi_piov4], linewidth=0.1, color='green')
ax1.plot(quad_x_1[0:5.6194e4],quad_y_1[0:5.6194e4],color='blue',linewidth=0.1)
ax1.plot(quad_x_2[0:5.6194e4],quad_y_2[0:5.6194e4],color='green',linewidth=0.1)
ax1.plot(sq_line_x_1, sq_line_y_1, color='red', linewidth=0.1)
ax1.plot(sq_line_x_2, sq_line_y_2, color='red', linewidth=0.1)

#ax1.tick_params(labelsize=30)
#ax1.set_xlim(-r2-1,r2+1 )
#ax1.set_ylim(-r2-1, r2+1)
ax1.set_xlim(-5,5)
ax1.set_ylim(-5,5)
#ax1.xaxis.set_ticks(np.append(np.arange(-r2-1, r2+1, 25), [0]))
#ax1.yaxis.set_ticks(np.append(np.arange(-r2-1, r2+1, 25), [0]))
#tics = ax1.xaxis.get_majorticklocs()

#ax1.set_xlabel('cm', fontsize=30)
#ax1.set_ylabel('cm', fontsize=30)

#ax2.set_ylim(-r2-1, r2+1)
ax2.set_ylim(-5,5)
#ax2.tick_params(labelsize=30)
#ax2.yaxis.set_ticks(np.append(np.arange(-r2-1, r2+1, 25), [0]))

#ax3.set_xlim(-r2-1, r2+1)
ax3.set_xlim(-5,5)
#ax3.tick_params(labelsize=30)
#ax3.xaxis.set_ticks(np.append(np.arange(-r2-1, r2+1, 25), [0]))

#ax2.set_ylabel('cm', fontsize=30)
#ax3.set_xlabel('cm', fontsize=30)

#fig.savefig('spiral_2.699mx2.699m_5mm_wire_taper.pdf', dpi=100, bbox_inches='tight')
#fig.savefig('spiral_testsize_balun_thicker.pdf', dpi=100, bbox_inches='tight')

#np.savetxt('bluearm_1.csv', np.c_[x[phi_piov2], y[phi_piov2]], delimiter=',')
#np.savetxt('bluearm_2.csv', np.c_[x1,y1], delimiter=',')
#np.savetxt('bluearm_taper.csv', np.c_[quad_x_1, quad_y_1], delimiter=',')

#np.savetxt('greenarm_1.csv', np.c_[x2, y2], delimiter=',')
#np.savetxt('greenarm_2.csv', np.c_[x2_2[phi_piov2], y2_2[phi_piov2]], delimiter=',')
#np.savetxt('greenarm_taper.csv', np.c_[quad_x_2, quad_y_2], delimiter=',')
