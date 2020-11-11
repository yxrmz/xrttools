# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev, Roman Chernikov"
__date__ = "22 Jan 2016"
import numpy as np
import matplotlib.pyplot as plt
# path to xrt:
import os, sys; sys.path.append(os.path.join('..', '..', '..'))  # analysis:ignore
import xrt.backends.raycing.materials as rm

def calc_vectors(theta, alphaDeg, geom):
    alpha = np.radians(alphaDeg)
    s0 = (np.zeros_like(theta), np.cos(theta+alpha), -np.sin(theta+alpha))
    sh = (np.zeros_like(theta), np.cos(theta-alpha), np.sin(theta-alpha))
    if geom.startswith('Bragg'):
        n = (0, 0, 1)  # outward surface normal
    else:
        n = (0, -1, 0)  # outward surface normal
    hn = (0, np.sin(alpha), np.cos(alpha))  # outward Bragg normal
    gamma0 = sum(i*j for i, j in zip(n, s0))
    gammah = sum(i*j for i, j in zip(n, sh))
    hns0 = sum(i*j for i, j in zip(hn, s0))
    return gamma0, gammah, hns0

#crystalType = 'Si'
crystalType = 'Ge'
hkl = (1, 1, 1)

if crystalType == 'Si':
    crystal = rm.CrystalSi(hkl=hkl)
elif crystalType == 'Ge':
    crystal = rm.CrystalDiamond(hkl=hkl, d=5.657, elements='Ge')

E = 8900
dtheta = np.linspace(-20, 80, 501)
#dtheta = np.linspace(-100, 300, 501)
theta = crystal.get_Bragg_angle(E) + dtheta*1e-6
asymmDeg = 0.  # Degrees

g0, gh, hs0 = calc_vectors(theta, asymmDeg, 'Bragg')
curS, curP = crystal.get_amplitude(E, g0, gh, hs0)
#curS, curP = crystal.get_amplitude(E, np.sin(theta))
#print(crystal.get_a())
print(crystal.get_F_chi(E, 0.5/crystal.d))
print(u'Darwin width at E={0:.0f} eV is {1:.5f} µrad for s-polarization'.
      format(E, crystal.get_Darwin_width(E) * 1e6))

plt.plot(dtheta, abs(curS)**2, 'r', dtheta, abs(curP)**2, 'b')
plt.gca().set_xlabel(u'$\\theta - \\theta_{B}$ (µrad)')
plt.gca().set_ylabel(r'reflectivity')
plt.show()
