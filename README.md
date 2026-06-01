# mieshah
# This Python package calculates light scattering properties/parameters of spheres by using Mie theory. 
Initial version was developed from a mie theory program originally written in FORTRAN and published in the paper: Ghanshyam A. Shah, "Numerical Methods for Mie Theory of Scattering by a Sphere",Kodaikanal Obs. Bull. Soc.(1977) 2, 42-63. In this major updated version has been updated with modern numerical calculation to provide better accuracy in the result.

- Developed by Dwaipayan Deb (2026)

## Why this project?

While standard Mie scattering packages like `PyMieScatt` or `miepython` are excellent for scattering calculations, `mieshah` is designed to simplify, automate, and speed up calculations for both **monodisperse** (single particle) and **polydisperse** (particle size distribution) scenarios.

* **Identical, Validated Results:** `mieshah` implements the standard Mie scattering equations (using Wiscombe's recurrence criteria), yielding results that are **numerically identical** to other established packages like `PyMieScatt` and `miepython`.
* **Built-in Symbolic Size Distribution (Polydisperse):** Instead of writing complex loops to manually discretize and integrate size distributions, you can pass any arbitrary frequency distribution function as a simple symbolic string (e.g., `f="x**-2"`). The package automatically handles discretization and integration.
* **Physically Accurate Polydisperse Averages:** Automatically applies the correct physical weighting (e.g., ratio-of-averages for bulk albedo and scattering cross-section weighting for the phase function and intensities), preventing incorrect flat arithmetic averaging of bulk optical properties.
* **Streamlined Single-Particle Analysis (Monodisperse):** For single-particle calculations, a single initialization automatically computes all efficiency factors ($Q_{\text{ext}}$, $Q_{\text{sca}}$, $Q_{\text{abs}}$, $Q_{\text{pr}}$, $Q_{\text{bak}}$), the asymmetry parameter, polarization, and angular phase function simultaneously, retrieving all relevant properties in one step.
* **Angular Windowing (`theta`):** For both single-particle and polydisperse cases, you can specify an angular window (e.g., `theta=[10, 45]`) to compute scattering parameters only in the region of interest, significantly reducing computation time and output file size.
* **Automated Structured Output:** Automatically logs bulk averages (`mie1.out`) and angular profiles (`mie2.csv`) to files for easy plotting or post-processing, avoiding the need to write custom CSV exporters in your scripts.

## Cite the code (APA style): 

Deb, D. (2026). mieshah: Calculate light scattering properties/parameters of spheres by using Mie theory (Version 1.0.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.15380219

Install command: 
---------------
`pip install mieshah`


Use example:
------------
```
import mieshah as ms
from matplotlib import pyplot as plt

# reff-> effective particle radius (microns), wl-> wavelength (microns), m-> complex refractive index (real, imaginary), 
# f-> size distribution function, incr-> increment for size distribution function
mymie = ms.miescatter(reff=[0.1,1], wl=6.283185307,m=(1.5,0),f="x**-2",incr=0.01)  # With size distribution function
#mymie = ms.miescatter(reff=100, wl=6.283185307,m=(1.5,0.0)) # Without size distribution function (single particle)

print(mymie.reff)
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


## New feature: `theta` input argument in v0.0.3

The `miescatter` class now supports an optional `theta` argument in the constructor, which sets the angular computation window for phase function outputs.

### Usage

```python
from miesh2 import miescatter

mies = miescatter(
    reff=[1, 5],
    wl=0.5,
    m=(1.5, 0.01),
    f='x**-2',
    incr=0.1,
    theta=[10, 45]
)
```

- `theta=[min,max]` runs the scattering phase calculation from `min` degrees to `max` degrees.
- If `theta` is omitted, default range is `[0,180]`.
- `theta` must be a list of two values; otherwise the code exits with a message.
- However single `int` value is allowed e.g. `theta=45`

## Behavior

- With `theta=[10,45]`, the method computes results only for angles 10 through 45 degrees.
- Internally, `miecalc()` iterates `for ITH in range(self.th_min+1,self.th_max+2)` and converts each angle to radians for phase calculations.

## Output

- `mie1.out` contains global sphere averaged optical parameters:
  - `X`, `QSCA`, `QEXT`, `QABS`, `ALBED`, `ASYM`, `QPR`, `QBAK`.
- `mie2.csv` contains per-angle data:
  - `theta`, `I_perp`, `I_para`, `Polar`, `p_theta`.

## Key Improvements in `pymieshah` (v1.0.0 vs v0.0.3)

`pymieshah` (v1.0.0) introduces significant performance, accuracy, and code modernization improvements over the older version (`v0.0.3`). These improvements affect execution speed, physical correctness of size-averaged quantities, and numerical stability:

### 1. $N \times$ Computational Speedup via Parameter Precalculation
* **Old Behavior (`v0.0.3`):** Single-particle parameters (Mie coefficients $a_n, b_n$ and efficiencies) were recalculated inside the angular loop for every angle $\theta$. For $N$ angles and $M$ size bins, the recurrence relations were evaluated $N \times M$ times.
* **New Behavior (`v1.0.0`):** Single-particle parameters for all size bins are precalculated and cached exactly **once** before entering the angular loop. The angular loop now only performs the lightweight sum over Legendre polynomials.
* **Impact:** For a full sweep of $N$ angles (e.g., $181$ angles from $0^\circ$ to $180^\circ$), this results in a speedup of approximately **$180\times$** for polydisperse calculations.

### 2. Correct Physical Weighting for Size Distributions
* **Albedo ($\text{ALBED}$):** Corrected to be the ratio of the average scattering efficiency to the average extinction efficiency ($\langle Q_{\text{sca}} \rangle / \langle Q_{\text{ext}} \rangle$) rather than the simple average of individual albedos (average of ratios):
  $$\text{Albedo}_{\text{avg}} = \frac{\sum Q_{\text{sca}}(r) f(r) \Delta r}{\sum Q_{\text{ext}}(r) f(r) \Delta r}$$
* **Phase Function ($P(\theta)$) and Intensities ($I_{\parallel}, I_{\perp}$):** Corrected to be weighted by the scattering cross-section ($C_{\text{sca}}(r) \propto Q_{\text{sca}}(r) \cdot x(r)^2$) rather than a flat arithmetic average over the frequency distribution $f(r)\Delta r$. This ensures that larger or more strongly scattering particles correctly dominate the collective phase function:
  $$P_{\text{avg}}(\theta) = \frac{\sum P(\theta, r) C_{\text{sca}}(r) f(r) \Delta r}{\sum C_{\text{sca}}(r) f(r) \Delta r}$$

### 3. Modernized Algorithm & Numerical Stability
* **Legacy Code Removal:** Replaced the legacy `dimpy`-based fixed array allocations (e.g., `dim(21001)`) with native, dynamic NumPy complex arrays (`complex128`).
* **Wiscombe Termination Criterion:** The recurrence termination limit is now dynamically computed using Wiscombe's criterion:
  $$n_{\text{stop}} = x + 4 x^{1/3} + 2$$
  This prevents unnecessary iterations, avoids array overflow, and ensures numerical stability for large size parameters.

## Dependencies

- `numpy`
- `sympy`
- `dimpy` (or replacement array initialization)

## Notes

- If `reff` is a range and `f` is supplied, an effective weighted average (frequency distribution) is computed.
- If `reff` is a single value, `f` should be omitted.



# Zenodo Release

Zenodo project doi:https://doi.org/10.5281/zenodo.15380219

