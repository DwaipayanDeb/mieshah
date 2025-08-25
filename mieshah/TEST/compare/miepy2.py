import numpy as np
import miepython
import matplotlib.pyplot as plt
from tablefile import *

f1=file("Hapke_5.7a.csv",",") # Delimter is comma (second argument)
cols=f1.read("c/l") # Reads columns as lists

# Parameters
m = 1.50 + 0.0j            # Refractive index
wavelength = 0.55          # Wavelength in microns
radius = 8.75352187        # Particle radius in microns

# Size parameter
x = 2 * np.pi * radius / wavelength
print("X=", x)

# Scattering angles
angles_deg = np.linspace(0, 180, 90)  # degrees
angles_rad = np.radians(angles_deg)    # radians
mu = np.cos(angles_rad)

# Prepare arrays
S1 = np.zeros_like(mu, dtype=complex)
S2 = np.zeros_like(mu, dtype=complex)

# Calculate S1 and S2 using miepython
for i in range(len(mu)):
    S1[i], S2[i] = miepython.mie_S1_S2(m, x, mu[i])

# Intensities
I_perp = np.abs(S1)**2
I_parallel = np.abs(S2)**2
DOP = (I_perp - I_parallel) / (I_perp + I_parallel)
intensity = (I_parallel + I_perp) / 2

# Phase function normalization
phase_function = intensity / np.sum(intensity * np.sin(angles_rad))
angles_deg2 = []
for x in cols[0]:
    angles_deg2.append(180-x)
# Plot
plt.figure(figsize=(8,6))
plt.yscale("log")
plt.plot(angles_deg, phase_function, label='Miepython', color='red')
plt.xlim(0, 180)
plt.ylim(1e-4,1e3)
plt.plot(angles_deg2, cols[1], label='Hapke', color='blue')
plt.xlabel(r'Scattering angle ${\theta} (degrees)$')
plt.ylabel(r'Phase function $p({\theta})$')
plt.title('Mie Scattering Intensities (Miepython v/s Hapke Fig5.7a)')
plt.text(82, 50, "X=100", fontsize=12)
plt.text(78, 25, "m=1.5+0.0j", fontsize=12)
plt.legend()
plt.grid(True)
plt.show()
