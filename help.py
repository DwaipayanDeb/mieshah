class Help:
    """Class containing detailed usage information for the mieshah package."""
    
    @staticmethod
    def show_all():
        help()

    @staticmethod
    def show_miescatter():
        print("""
miescatter Class (from pymieshah)
=================================
Performs Mie scattering calculations for spherical particles at a single wavelength.
Supports monodisperse (single size) and polydisperse (range of sizes with distribution) cases.

Version: 1.1.1

Initialization Parameters:
  reff (float, int, or list) : Particle radius (in microns).
                               - A float or int (e.g., 0.1) for monodisperse.
                               - A list [min, max] (e.g., [0.01, 1.0]) for polydisperse.
  wl (float)                 : Incident light wavelength in microns (mandatory).
  m (tuple)                  : Complex refractive index (n, k) as a tuple (e.g., (1.403, 0.024)) (mandatory).
  incr (float, optional)     : Particle size increment for range calculation. Defaults to (max - min) / 100.
  f (str, optional)          : Size distribution expression as a string in terms of 'r' or 'x' (e.g., 'r**-2').
                               Mandatory if 'reff' is a list.
  theta (int, float, or list): Scattering angle(s) in degrees. Three accepted forms:
                               - theta=30          : single angle at 30 degrees.
                               - theta=[10, 45]    : integer steps 10, 11, 12, ..., 45 (inclusive).
                               - theta=[10, 30, 20]: 20 linearly spaced angles from 10 to 30 deg
                                                     (uses numpy.linspace, so fractional degrees allowed).
                               Default: full range [0, 180] in 1-degree integer steps.
  verbose (bool, optional)   : If True, prints progress status (default: True).

Calculated Properties:
  - X, QEXT, QSCA, QABS, ALBED, ASYM, QPR, QBAK, RHO, SCA, r_eff
  - I_perp, I_parl, theta, p_theta, Polar (lists corresponding to angular results)

Output Files:
  - 'mie1.csv'  : Overall scattering parameters at the reference theta angle.
  - 'mie2.csv'  : Angular distribution metrics (intensity, phase function, polarization).

Examples:
  miescatter(reff=0.5, wl=0.55, m=(1.5, 0.01), theta=90)
  miescatter(reff=0.5, wl=0.55, m=(1.5, 0.01), theta=[30, 150])
  miescatter(reff=0.5, wl=0.55, m=(1.5, 0.01), theta=[10, 30, 20])
"""
)

    @staticmethod
    def show_specfile():
        print("""
specfile Class (from specfile)
==============================
Reads, parses, and scales spectral refractive index data (n, k) and wavelengths/wavenumbers from text files.

Initialization Parameters:
  filename (str)             : Path to the spectrum data file (mandatory).
  sep (str, optional)        : Column delimiter (default: None, which auto-detects delimiter).
  wlcol (int, optional)      : 0-indexed column index for wavelength data.
  wlscale (numeric, optional): Scaling multiplier applied to wavelengths/wavenumbers (default: 1).
  ncol (int)                 : 0-indexed column index for refractive index real part (n) (mandatory).
  kcol (int)                 : 0-indexed column index for refractive index imaginary part (k) (mandatory).
  wncol (int, optional)      : 0-indexed column index for wavenumber data.
  
  Note: Specify either wlcol or wncol, but not both.

Methods:
  readspec()                 : Returns the list of scaled wavelengths.
  nktuple()                  : Returns the list of (n, k) tuples.
  list()                     : Returns a tuple (wavelength_list, n_k_tuple_list).
""")

    @staticmethod
    def show_spectrum():
        print("""
spectrum Class (from specfile)
==============================
Performs Mie scattering calculations across a wavelength spectrum using data from a specfile.

Version: 1.1.1

Initialization Parameters:
  data (specfile)            : A specfile instance containing the spectrum (mandatory).
  reff (numeric or list)     : Effective radius or range [min, max] (mandatory).
  f (str, optional)          : Size/frequency distribution function expression as a string (e.g., 'r**-2').
  theta (numeric or list)    : Scattering angle in degrees. Accepted forms:
                               - theta=90          : single angle at 90 degrees.
                               - theta=[10, 45]    : integer steps 10 to 45 (inclusive).
                               - theta=[10, 30, 20]: 20 linearly spaced angles 10 to 30 deg.
                               Default: 180.
  verbose (bool, optional)   : If True, prints status messages during calculations (default: False).

Methods:
  save(file1=None, file2=None) : Computes the spectrum and saves to files (default: 'Spec_mie1.csv', 'Spec_mie2.csv').
""")


def help():
    """Prints the help documentation for the entire mieshah package."""
    help_text = """
================================================================================
                             MIESHAH HELP  (v1.1.1)
================================================================================
mieshah is a Python package for calculating light scattering properties and
parameters of spherical particles using Mie theory. It supports both monodisperse
and polydisperse particle size distributions.

The package contains three main components:
1. miescatter (from pymieshah): Calculates scattering at a single wavelength.
2. specfile (from specfile): Parses and wraps spectral index datasets from files.
3. spectrum (from specfile): Performs scattering computations over a spectrum.

For detailed documentation on specific components, use:
- Help.show_miescatter() : For single wavelength calculations.
- Help.show_specfile()    : For importing spectral data files.
- Help.show_spectrum()    : For computations over a spectrum.
- Help.show_all()         : Show everything.
"""
    print(help_text)
    Help.show_miescatter()
    Help.show_specfile()
    Help.show_spectrum()
