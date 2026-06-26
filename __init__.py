"""
mieshah

A Python package for calculating light scattering properties and parameters
of spherical particles using Mie theory. Supports both monodisperse and
polydisperse particle size distributions.
"""

from .pymieshah import miescatter
from .specfile import specfile
from .specfile import spectrum
from .help import Help
from .help import help

__version__ = "1.1.1"
__author__ = "Dwaipayan Deb"
__all__ = ["miescatter", "specfile", "spectrum", "Help", "help"]