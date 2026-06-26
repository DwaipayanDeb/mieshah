import math
from tablefile import *
from .pymieshah import miescatter

class specfile(file):
    """
    Reader and parser for spectral refractive index and wavelength files.

    Inherits from the `tablefile.file` class.
    """
    def __init__(self, filename, sep=None, wlcol=None, wlscale=1, ncol=None, kcol=None, wncol=None):
        """
        Initialize the specfile object.

        Parameters
        ----------
        filename : str
            Path to the spectrum data file.
        sep : str, optional
            Delimiter string to split columns (default: None, which auto-detects).
        wlcol : int, optional
            0-indexed column index containing wavelength data.
        wlscale : int or float, optional
            Scaling factor applied to the wavelength or wavenumber (default: 1).
        ncol : int
            0-indexed column index containing the real part (n) of refractive index.
        kcol : int
            0-indexed column index containing the imaginary part (k) of refractive index.
        wncol : int, optional
            0-indexed column index containing wavenumber data.
        """
        if not isinstance(filename, str):
            raise TypeError("filename must be a string path to the spectrum data file")
        '''if not isinstance(sep, str):
            pass
            #raise TypeError("sep must be a string delimiter")'''
        if wlcol is not None and not isinstance(wlcol, int):
            raise TypeError("wlcol must be an integer column index")
        if wncol is not None and not isinstance(wncol, int):
            raise TypeError("wncol must be an integer column index")
        if ncol is not None and not isinstance(ncol, int):
            raise TypeError("ncol must be an integer column index")
        if kcol is not None and not isinstance(kcol, int):
            raise TypeError("kcol must be an integer column index")
        if not isinstance(wlscale, (int, float)):
            raise TypeError("wlscale must be a numeric scaling factor")
        if ncol is None or kcol is None:
            raise ValueError("ncol and kcol are mandatory for the refractive index columns")
        if wlcol is None and wncol is None:
            raise ValueError("Either wlcol or wncol must be specified to read the spectral wavelength/wn data")
        if wlcol is not None and wncol is not None:
            import sys
            print("Error: Specify only one of wlcol or wncol, not both.")
            sys.exit(1)

        super().__init__(filename, sep)
        self.wlcol = wlcol
        self.wlscale = wlscale
        self.wncol = wncol
        self.ncol = ncol
        self.kcol = kcol

    def nktuple(self):
        """
        Read real and imaginary refractive index columns from the file.

        Returns
        -------
        list of tuple
            List of (n, k) tuples representing complex refractive index entries.
        """
        cols = self.readcols()
        m_tuple_list = []
        for i in range(len(cols[self.ncol])):
            m_tuple_list.append((cols[self.ncol][i], cols[self.kcol][i]))
        return m_tuple_list

    def readspec(self):
        """
        Read the wavelength or wavenumber column, applying the scaling factor.

        Returns
        -------
        list of float
            List of scaled wavelengths.
        """
        cols = self.readcols()
        if self.wlcol is not None:
            return [(float(i) * self.wlscale) for i in cols[self.wlcol]]
        if self.wncol is not None:
            return [(1 / float(i)) * self.wlscale for i in cols[self.wncol]]
        raise RuntimeError("Internal error: no spectrum column configured")

    def list(self):
        """
        Convenience method to retrieve both wavelengths and complex refractive indices.

        Returns
        -------
        tuple
            A tuple (wavelength_list, n_k_tuple_list).
        """
        wl_list = self.readspec()
        m_tuple_list = self.nktuple()
        return wl_list, m_tuple_list



class spectrum:
    """
    Computes Mie scattering spectra for spherical particles using parsed data from a specfile.
    """
    def __init__(self, data, reff=None, f=None, theta=None, verbose=False):
        """
        Initialize the spectrum object.

        Parameters
        ----------
        data : specfile
            An instance of the specfile class containing the spectrum and indices.
        reff : float, int, or list
            Effective radius. Can be numeric (monodisperse) or a list [min, max] (polydisperse).
        f : str, optional
            Frequency distribution function expression (e.g. 'r**-2'). Required if reff is a list.
        theta : int, float, or list, optional
            Scattering angle(s) in degrees, or range [min, max] (default: 180).
        verbose : bool, optional
            If True, prints computation messages to the console (default: False).
        """
        if data is None:
            raise ValueError("data is required and must be a specfile instance")
        if not hasattr(data, 'list'):
            raise TypeError("data must be a specfile-like object with a .list() method")
        if reff is None:
            raise ValueError("reff is required and must be a float, int, or [min, max] list")
        if not isinstance(reff, (int, float, list)):
            raise TypeError("reff must be numeric or a list of two numeric values")
        if isinstance(reff, list) and len(reff) != 2:
            raise ValueError("reff list must contain exactly two values: [min, max]")
        if f is not None and not isinstance(f, str):
            raise TypeError("f must be a string frequency distribution expression")
        if theta is None:
            theta = 0
            print("\t-> theta is not given, proceeding with default 0 deg. (forward scattering direction).")
        if not isinstance(theta, (int, float)):
            raise TypeError("theta must be a single valued int or float for spectrum generation")
        if isinstance(theta, list) and len(theta) != 2:
            raise ValueError("in case of spectrum generation theta must be a single valued float or int")
        if not isinstance(verbose, bool):
            raise TypeError("verbose must be a boolean value")

        self.data = data
        self.reff = reff
        self.f = f
        self.theta = theta
        self.verbose = verbose

        # Spectral output arrays (one entry per wavelength)
        self.wl = []
        self.X = []
        self.QSCA = []
        self.QEXT = []
        self.QABS = []
        self.ALBED = []
        self.ASYM = []
        self.QPR = []
        self.QBAK = []
        self.SCA = []
        self.r_eff = []
        self.I_perp = []
        self.I_parl = []
        self.Polar = []
        self.p_theta = []

        self.available = [
            'wl', 'X', 'QSCA', 'QEXT', 'QABS', 'ALBED', 'ASYM', 'QPR',
            'QBAK', 'SCA', 'r_eff', 'I_perp', 'I_parl', 'Polar', 'p_theta'
        ]
        # Precompute spectrum so attributes are available without calling save()
        try:
            self._compute_spectrum()
        except Exception:
            # If precomputation fails, keep object usable and defer computation to save()
            pass

    def save(self, file1=None, file2=None):
        """
        Compute the Mie scattering properties and save the results to files.

        Parameters
        ----------
        file1 : str, optional
            Output CSV file name for general efficiencies (default: "Spec_mie1.csv").
        file2 : str, optional
            Output CSV file name for angular distribution parameters (default: "Spec_mie2.csv").
        """
        # Provide defaults for missing output filenames
        if file1 is None:
            file1 = "Spec_mie1.csv"
        if file2 is None:
            file2 = "Spec_mie2.csv"

        # Ensure spectrum is computed
        if not self.wl:
            self._compute_spectrum()

        f1 = open(file1, "w")
        f2 = open(file2, "w")
        f1.write("X,WL,QSCA,QEXT,QABS,ALBED,ASYM,QPR,QBAK,SCA,r_eff\n")
        f2.write("wl,theta,I_perp,I_parl,Polar,p_theta\n")

        # Write using the precomputed lists
        for i, wl in enumerate(self.wl):
            X = self.X[i]
            QSCA = self.QSCA[i]
            QEXT = self.QEXT[i]
            QABS = self.QABS[i]
            ALBED = self.ALBED[i]
            ASYM = self.ASYM[i]
            QPR = self.QPR[i]
            QBAK = self.QBAK[i]
            SCA = self.SCA[i]
            r_eff = self.r_eff[i]

            Iperp = self.I_perp[i]
            Iparl = self.I_parl[i]
            Polar = self.Polar[i]
            p_theta = self.p_theta[i]

            f1.write(f"{X},{wl},{QSCA},{QEXT},{QABS},{ALBED},{ASYM},{QPR},{QBAK},{SCA},{r_eff}\n")
            # Use the requested theta parameter for the theta column to match previous behavior
            f2.write(f"{wl},{self.theta},{Iperp},{Iparl},{Polar},{p_theta}\n")

        f1.close()
        f2.close()
        print(f"Successfully saved in {file1}")
        print(f"Successfully saved in {file2}")

    def _compute_spectrum(self):
        """Compute and populate spectral attribute lists without writing files."""
        # Reset lists
        self.wl = []
        self.X = []
        self.QSCA = []
        self.QEXT = []
        self.QABS = []
        self.ALBED = []
        self.ASYM = []
        self.QPR = []
        self.QBAK = []
        self.SCA = []
        self.r_eff = []
        self.I_perp = []
        self.I_parl = []
        self.Polar = []
        self.p_theta = []

        wl_list, m_tuple_list = self.data.list()
        #wl_list = [(float(i) * self.data.wlscale) for i in wl_list]

        for wl, m in zip(wl_list, m_tuple_list):
            mie = miescatter(reff=self.reff, f=self.f, wl=wl, m=m, theta=self.theta, verbose=self.verbose)

            self.wl.append(wl)
            self.X.append(mie.X)
            self.QSCA.append(mie.QSCA)
            self.QEXT.append(mie.QEXT)
            self.QABS.append(mie.QABS)
            self.ALBED.append(mie.ALBED)
            self.ASYM.append(mie.ASYM)
            self.QPR.append(mie.QPR)
            self.QBAK.append(mie.QBAK)
            self.SCA.append(mie.SCA)
            self.r_eff.append(mie.r_eff)
            self.I_perp.append(mie.I_perp[0] if mie.I_perp else None)
            self.I_parl.append(mie.I_parl[0] if mie.I_parl else None)
            self.Polar.append(mie.Polar[0] if mie.Polar else None)
            self.p_theta.append(mie.p_theta[0] if mie.p_theta else None)