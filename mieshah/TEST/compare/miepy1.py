import numpy as np
import mieshah as ms
import matplotlib.pyplot as plt
from tablefile import *

f1=file("Hapke_5.7a.csv",",")# Delimter is comma (second argument)
cols=f1.read("c/l") # Reads columns as lists
# Parameters
miescatt = ms.miescatter(ps=8.75352187, wl=0.55, m=(1.5, 0.0)) # ps=particle size in microns, wl=wavelength in microns, m=(real, imag) refractive index
print("X=",miescatt.X)

angles_deg2 = []
for x in cols[0]:
    angles_deg2.append(180-x)
plt.figure(figsize=(8,6))    
plt.yscale("log")
plt.plot(miescatt.theta[::2], miescatt.p_theta[::2], label=r'mieshah', color='red')
plt.plot(angles_deg2, cols[1], label='Hapke', color='blue')
plt.xlim(0, 180)
plt.ylim(1e-4,1e3)
plt.xlabel(r'Scattering angle ${\theta} (degrees)$')
plt.ylabel(r'Phase function $p({\theta})$')
plt.title('Mie Scattering Intensities (mieshah v/s Hapke Fig5.7a)')
plt.text(82, 50, "X=100", fontsize=12)
plt.text(78, 25, "m=1.5+0.0j", fontsize=12)
plt.legend()
plt.grid(True)
plt.show()


