# mieshah
# This Python package calculates light scattering properties/parameters of spheres by using Mie theory. 
This has been developed from a mie theory program originally written in FORTRAN and published in the paper: Ghanshyam A. Shah, "Numerical Methods for Mie Theory of Scattering by a Sphere",Kodaikanal Obs. Bull. Soc.(1977) 2, 42-63. 
- Python form developed by Dwaipayan Deb (2025)

Install command: 
---------------
`pip install mieshah`


Use example:
------------
```
import mieshah as ms
from matplotlib import pyplot as plt

# ps-> particle radius(microns), wl-> wavelength (microns), m-> complex refractive index (real,imaginary), 
# f-> size distribution function, incr-> increment for size distribution function
mymie = ms.miescatter(ps=[0.1,1], wl=6.283185307,m=(1.5,0),f="x**-2",incr=0.01)  # With size distribution function
#mymie = ms.miescatter(ps=100, wl=6.283185307,m=(1.5,0.0)) # Without size distribution function (single particle)

print(mymie.ps)
print(mymie.wl)
print(mymie.m)
print(mymie.f)
print(mymie.X) # Size parameter
print(mymie.ALBED) # Albedo
print(mymie.QSCA) # Scattering efficiency
print(mymie.QEXT) # Extinction efficiency
print(mymie.QBAK) # Backscattering efficiency
print(mymie.QABS) # Absorption efficiency
print(mymie.QPR) # Radiation pressure efficiency
print(mymie.I_perp) # Intensity perpendicular to the plane of incidence
print(mymie.I_parl) # Intensity parallel to the plane of incidence
print(mymie.Polar) # Degree of linear polarization
print(mymie.p_theta) # Phase function
print(mymie.theta) # Scattering angle in degrees

plt.plot(mymie.theta[::2], mymie.Polar[::2])
plt.xlabel('Theta (degrees)')
plt.ylabel('Polarization')
plt.title('Degree of Linear Polarization')
plt.show()
plt.plot(mymie.theta[::2], mymie.p_theta[::2])
plt.yscale('log')    
plt.xlabel('Theta (degrees)')
plt.ylabel('Phase Function')
plt.title('Phase Function')
plt.show()
```
# Zenodo Release

Zenodo project doi:https://doi.org/10.5281/zenodo.15380220

