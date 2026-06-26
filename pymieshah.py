#v1.1.1
from sympy import symbols, sympify
import numpy as np
from dimpy import *

class miescatter:
    """
    Class for Mie scattering calculations for spherical particles.

    Parameters
    ----------
    reff : float, int, or list
        Particle size or range of particle sizes.
    wl : float
        Wavelength of incident light.
    m : tuple
        Complex refractive index as (real, imaginary).
    incr : float, optional
        Increment for particle size distribution.
    f : str, optional
        Frequency distribution function as a string in terms of 'r' or 'x'
        (e.g., 'r**-2' or 'x**-2').
    theta : int, float, or list, optional
        Scattering angle(s) in degrees. Accepted forms:
          - theta=30            : single angle at 30 degrees.
          - theta=[10, 45]      : integer steps from 10 to 45 (inclusive).
          - theta=[10, 30, 20]  : 20 linearly spaced angles from 10 to 30
                                  (equivalent to numpy.linspace(10, 30, 20)).
        Default: full range 0-180 degrees in 1-degree steps.
    verbose : bool, optional
        If True (default), print progress messages to terminal.
        Set to False to suppress all terminal output.

    Attributes
    ----------
    r_eff : float
        Effective radius of the particle size distribution.
    """
    def __init__(self, **kwargs):
        """
        Initialize the miescatter object with input parameters.
        """
        self.x = symbols('x')
        self.r = symbols('r')
        self.reff = kwargs.get('reff', None)
        self.wl = kwargs.get('wl', None)
        self.m = kwargs.get('m', None)
        self.incr = kwargs.get('incr', None)
        self.verbose = kwargs.get('verbose', True)
        self.theta_in=kwargs.get('theta', None)
        self.I_perp=[]
        self.I_parl=[]
        self.theta=[]
        self.p_theta=[]
        self.Polar=[]  
        self.r_eff=None


        # Flag to distinguish the three theta input modes
        self._theta_linspace = False   # True when theta=[lo, hi, n]

        if self.theta_in is not None:
            if isinstance(self.theta_in, list) and len(self.theta_in) == 3:
                # Linspace mode: [lower_range, upper_range, no_of_split]
                lo, hi, n = self.theta_in
                if not all(isinstance(v, (int, float)) for v in [lo, hi, n]):
                    print("Invalid input\nWhen theta is a 3-element list all three values must be numeric.")
                    print("Example: theta=[10, 30, 20]")
                    print("Exiting...")
                    exit()
                if int(n) < 2:
                    print("Invalid input\nThe number of points (third element) must be at least 2.")
                    print("Exiting...")
                    exit()
                self.th_min = min(lo, hi)
                self.th_max = max(lo, hi)
                self._theta_arr = np.linspace(min(lo, hi), max(lo, hi), int(n))
                self._theta_linspace = True
            elif isinstance(self.theta_in, list) and len(self.theta_in) == 2:
                self.th_min = min(self.theta_in)
                self.th_max = max(self.theta_in)
            elif isinstance(self.theta_in, (float, int)):
                self.th_min = int(self.theta_in)
            else:
                print("Invalid input\nPlease enter a valid theta (e.g. theta=30, theta=[10,45], or theta=[10,30,20])")
                print("Exiting...")
                exit()
        else:
            self.th_min = 0
            self.th_max = 180

        if self.reff==None or self.wl==None or type(self.m)!=tuple:
            print("Invalid input\nPlease enter a valid reff, wl, and m (e.g. reff=0.1 or reff=[0.01,0.1], wl=0.365, m=(1.403,0.024))")
            print("Exiting...")
            exit()
            

        # Convert f string to a SymPy expression; supports 'r' or 'x' as variable
        f_expr = kwargs.get('f', None)
        if f_expr is not None:
            self.f = sympify(f_expr)
            # Determine which symbol the user used in their expression
            if self.r in self.f.free_symbols:
                self.f_var = self.r
            else:
                self.f_var = self.x
        else:
            self.f = None
            self.f_var = self.x

        if type(self.reff) == list and self.f is not None:
            if len(self.reff) != 2:
                print("Invalid input\nPlease enter a valid reff (e.g. reff=[0.01,0.1])")
                print("Exiting...")
                exit()
            self.reff_min = min(self.reff)
            self.reff_max = max(self.reff)
            if self.incr is None:
                self.incr = (self.reff_max - self.reff_min) / 100
                if self.verbose:
                    print("'incr' is set to default value:", self.incr)
        elif type(self.reff) ==float and self.f is not None:
            
            print("reff and f are not compatible\nAs single particle is entered no frequency distribution is allowed.\nExiting...")
            self.f = None
            exit()
        elif type(self.reff) ==int and self.f is not None:            
            print("reff and f are not compatible\nAs single particle is entered no frequency distribution is allowed.\nExiting...")
            self.f = None
            exit()
        elif type(self.reff) ==list and self.f is None:
            print("reff and f are not compatible\nAs a range of particle size is entered a frquency distribution function must be given (e.g. f='x**-1.5')\nExiting...")
            self.f = None
            exit()
        if self.f is not None and self.verbose:
            print("Please wait...")
        self.miecalc()

    def miecalc(self):
        """
        Perform Mie scattering calculations and write results to output files.
        """
        f1 = open("mie1.csv", "w")
        f2 = open("mie2.csv", "w")

        AMU1 = self.m[0]
        AMU2 = self.m[1]
        WL = self.wl
        DK = self.incr
        
        # relative refractive index in standard convention: m = n + i*k
        refrel = AMU1 + 1j * AMU2

        # Setup the particle size range (polydisperse or single)
        if type(self.reff) == list and self.f is not None:
            a_range = self.reff
            a_ = np.arange(a_range[0], a_range[1] + DK, DK)
        elif type(self.reff) == float or type(self.reff) == int:
            a_ = [self.reff]
        else:
            a_ = [self.reff]

        # 1. Precalculate single-particle parameters for all sizes
        mie_results = []
        num_reff = 0.0
        den_reff = 0.0
        for a in a_:
            if len(a_) != 1:
                frequency = float(self.f.subs({self.f_var: a}))
                num_reff += (a**3) * frequency * DK
                den_reff += (a**2) * frequency * DK
            else:
                frequency = 1.0

        if len(a_) != 1:
            self.r_eff = num_reff / den_reff if den_reff > 0.0 else 0.0
        else:
            self.r_eff = self.reff

        for a in a_:
            if len(a_) != 1:
                frequency = float(self.f.subs({self.f_var: a}))
            else:
                frequency = 1.0

            x = (2.0 * np.pi * a) / WL
            y = x * refrel
            ymod = abs(y)

            # Termination order (nstop) and starting order for downward recurrence (nmx)
            xstop = x + 4.0 * (x**0.3333) + 2.0
            nstop = int(xstop)
            nmx = int(max(xstop, ymod) + 15)

            # Logarithmic derivative of complex argument D(y) by downward recurrence
            d = np.zeros(nmx + 1, dtype=np.complex128)
            for n in range(nmx - 1, 0, -1):
                d[n-1] = n/y - 1.0 / (d[n] + n/y)

            # Riccati-Bessel functions of real argument x by forward recurrence
            psi0 = np.cos(x)
            psi1 = np.sin(x)
            chi0 = -np.sin(x)
            chi1 = np.cos(x)

            qsca_sum = 0.0
            qext_sum = 0.0
            g_sum = 0.0
            qbak_sum = 0.0
            sca_val = 0.0

            an_prev = 0.0 + 0.0j
            bn_prev = 0.0 + 0.0j

            an_list = []
            bn_list = []

            for n in range(1, nstop + 1):
                psi = (2.0 * n - 1.0) * psi1 / x - psi0
                chi = (2.0 * n - 1.0) * chi1 / x - chi0
                xi = psi - 1j * chi
                xi1 = psi1 - 1j * chi1

                # d[n] corresponds to D_n(y)
                an_num = ((d[n] / refrel) + n / x) * psi - psi1
                an_den = ((d[n] / refrel) + n / x) * xi - xi1
                an = an_num / an_den

                bn_num = (refrel * d[n] + n / x) * psi - psi1
                bn_den = (refrel * d[n] + n / x) * xi - xi1
                bn = bn_num / bn_den

                an_list.append(an)
                bn_list.append(bn)

                fn = 2 * n + 1
                qext_sum += fn * (an.real + bn.real)
                qsca_sum += fn * (abs(an)**2 + abs(bn)**2)
                qbak_sum += fn * ((-1)**n) * (an - bn)
                
                # SCA is used in PyMieShah
                sca_val += (n + 0.5) * (abs(an)**2 + abs(bn)**2)

                # gsca calculation
                term1 = (2 * n + 1) / (n * (n + 1)) * (an * np.conj(bn)).real
                g_sum += term1
                if n > 1:
                    term2 = (n - 1) * (n + 1) / n * (an_prev * np.conj(an) + bn_prev * np.conj(bn)).real
                    g_sum += term2

                an_prev = an
                bn_prev = bn

                psi0 = psi1
                psi1 = psi
                chi0 = chi1
                chi1 = chi

            qext = (2.0 / x**2) * qext_sum
            qsca = (2.0 / x**2) * qsca_sum
            qabs = qext - qsca
            albed = qsca / qext if qext > 0 else 0.0
            qbak = (abs(qbak_sum)**2) / (x**2)
            gsca = 2.0 * g_sum / qsca_sum if qsca_sum > 0 else 0.0
            qpr = qext - gsca * qsca
            rho = 2.0 * x * (AMU1 - 1.0)

            mie_results.append({
                'a': a,
                'x': x,
                'qext': qext,
                'qsca': qsca,
                'qabs': qabs,
                'albed': albed,
                'gsca': gsca,
                'qpr': qpr,
                'qbak': qbak,
                'rho': rho,
                'sca': sca_val,
                'nn': nstop,
                'an': an_list,
                'bn': bn_list,
                'frequency': frequency
            })

        # 2. Define the angular calculation nested function
        def mie_theta(THETA_DEG, a_range):
            SSS1 = 0.0
            SSS2 = 0.0
            tot_freq = 0.0
            tot_csca_freq = 0.0   # normaliser for Csca-weighted averages
            Phase_func_list = []
            Phase_func_wts = []   # per-particle Csca*f(a)*da weights for phase function
            
            QBAK_ = []
            QEXT_ = []
            QSCA_ = []
            QABS_ = []
            ASYM_ = []
            QPR_ = []
            RHO_ = []
            SCA_ = []
            X_ = []
            # accumulate numerator/denominator for ALBED separately
            QSCA_num_ = []
            QEXT_num_ = []

            THETA = THETA_DEG
            th_rad = THETA * np.pi / 180.0
            cth = np.cos(th_rad)

            # Loop over precalculated single-particle results
            for res in mie_results:
                x = res['x']
                an = res['an']
                bn = res['bn']
                nstop = res['nn']
                frequency = res['frequency']

                # Compute S1 and S2 at this angle
                pi_prev = 0.0
                pi_curr = 1.0

                # n = 1 term for S1 and S2
                s1 = 1.5 * (an[0] + cth * bn[0])
                s2 = 1.5 * (an[0] * cth + bn[0])

                for n in range(2, nstop + 1):
                    fn = (2.0 * n + 1.0) / (n * (n + 1.0))
                    pi_next = (cth * (2.0 * n - 1.0) * pi_curr - n * pi_prev) / (n - 1.0)
                    tau_curr = n * cth * pi_next - (n + 1.0) * pi_curr

                    s1 += fn * (an[n-1] * pi_next + bn[n-1] * tau_curr)
                    s2 += fn * (an[n-1] * tau_curr + bn[n-1] * pi_next)

                    pi_prev = pi_curr
                    pi_curr = pi_next

                ss1 = abs(s1)**2
                ss2 = abs(s2)**2
                
                # Retrieve precalculated efficiencies
                qext = res['qext']
                qsca = res['qsca']
                qabs = res['qabs']
                albed = res['albed']
                gsca = res['gsca']
                qpr = res['qpr']
                qbak = res['qbak']
                rho = res['rho']
                sca = res['sca']

                if len(a_) != 1:
                    # Csca * f(a) * da is the correct weight for phase-function and
                    # polarisation averaging; Csca proportional to qsca * x^2
                    csca_wt = qsca * (x**2) * frequency * DK

                    # Weight SSS1, SSS2 and phase function by Csca*f(a)*da
                    SSS1 += ss1 * csca_wt
                    SSS2 += ss2 * csca_wt
                    Phase_func_list.append(2.0 * (ss1 + ss2) / (qsca * (x**2)) * csca_wt)
                    Phase_func_wts.append(csca_wt)
                    tot_freq += frequency * DK
                    tot_csca_freq += csca_wt

                    if abs(THETA - self.th_min) < 1e-9:
                        w = frequency * DK
                        X_.append(x * w)
                        QABS_.append(qabs * w)
                        QSCA_.append(qsca * w)
                        QEXT_.append(qext * w)
                        QBAK_.append(qbak * w)
                        # Fix 1: accumulate numerator and denominator for ALBED separately
                        QSCA_num_.append(qsca * w)
                        QEXT_num_.append(qext * w)
                        ASYM_.append(gsca * csca_wt)
                        QPR_.append(qpr * csca_wt)
                        RHO_.append(rho * w)
                        SCA_.append(sca * w)
                else:
                    SSS1 = ss1
                    SSS2 = ss2
                    Phase_func_list.append(2.0 * (ss1 + ss2) / (qsca * (x**2)))
                    Phase_func_wts.append(1.0)
                    tot_freq = 1.0
                    tot_csca_freq = 1.0

                    if abs(THETA - self.th_min) < 1e-9:
                        X_.append(x)
                        QABS_.append(qabs)
                        QSCA_.append(qsca)
                        QEXT_.append(qext)
                        QBAK_.append(qbak)
                        QSCA_num_.append(qsca)
                        QEXT_num_.append(qext)
                        ASYM_.append(gsca)
                        QPR_.append(qpr)
                        RHO_.append(rho)
                        SCA_.append(sca)

            SSS1 /= tot_csca_freq
            SSS2 /= tot_csca_freq
            tss = SSS1 + SSS2
            # Fix 2: phase function normalised by total Csca*f(a)*da weight
            Phase_func = np.sum(Phase_func_list) / tot_csca_freq
            polar = (SSS1 - SSS2) / tss if tss > 0 else 0.0

            # Store the averaged efficiencies at THETA == self.th_min
            if len(a_) != 1 and abs(THETA - self.th_min) < 1e-9:
                self.X = np.sum(X_) / tot_freq
                self.QABS = np.sum(QABS_) / tot_freq
                self.QSCA = np.sum(QSCA_) / tot_freq
                self.QEXT = np.sum(QEXT_) / tot_freq
                # Fix 1: ALBED = <Qsca> / <Qext>  (ratio of averages, not average of ratios)
                self.ALBED = np.sum(QSCA_num_) / np.sum(QEXT_num_) if np.sum(QEXT_num_) > 0 else 0.0
                self.ASYM = np.sum(ASYM_) / tot_csca_freq
                self.QPR = np.sum(QPR_) / tot_csca_freq
                self.QBAK = np.sum(QBAK_) / tot_freq
                self.RHO = np.sum(RHO_) / tot_freq
                self.SCA = np.sum(SCA_) / tot_freq
                self.NN = nstop
            elif len(a_) == 1 and abs(THETA - self.th_min) < 1e-9:
                self.X = mie_results[0]['x']
                self.QABS = mie_results[0]['qext'] - mie_results[0]['qsca']
                self.QSCA = mie_results[0]['qsca']
                self.QEXT = mie_results[0]['qext']
                self.ALBED = mie_results[0]['albed']
                self.ASYM = mie_results[0]['gsca']
                self.QPR = mie_results[0]['qpr']
                self.QBAK = mie_results[0]['qbak']
                self.RHO = mie_results[0]['rho']
                self.SCA = mie_results[0]['sca']
                self.NN = nstop

            self.I_perp.append(SSS1)
            self.I_parl.append(SSS2)
            self.theta.append(THETA)
            self.p_theta.append(Phase_func)
            self.Polar.append(polar)

            f2.write(f"{THETA},{SSS1},{SSS2},{polar},{Phase_func}\n")

        # 3. Write header and execute the angular loop
        f2.write("theta,I_perp,I_parl,Polar,p_theta\n")

        if isinstance(self.theta_in, (float, int)):
            mie_theta(self.th_min, self.reff)
        elif self._theta_linspace:
            for theta_val in self._theta_arr:
                if self.verbose:
                    print(f"Calculating for: theta= {theta_val:.6g} deg.", end="\r", flush=True)
                mie_theta(theta_val, self.reff)
        else:
            for theta_val in range(self.th_min, self.th_max + 1, 1):
                if self.verbose:
                    print(f"Calculating for: theta= {theta_val} deg.", end="\r", flush=True)
                mie_theta(theta_val, self.reff)

        if self.verbose:
            print("\nProcess competed.\nPlease see the output files for results")

        f1.write(f"X,WL,QSCA,QEXT,QABS,ALBED,ASYM,QPR,QBAK,SCA,r_eff\n")
        f1.write(f"{self.X},{self.wl},{self.QSCA},{self.QEXT},{self.QABS},{self.ALBED},{self.ASYM},{self.QPR},{self.QBAK},{self.SCA},{self.r_eff}\n")

        f1.close()
        f2.close()