"""
mieshah

A Python package for calculating light scattering properties and parameters
of spherical particles using Mie theory. Supports both monodisperse and
polydisperse particle size distributions.
"""

from .pymieshah import miescatter

__version__ = "1.0.0"
__author__ = "Dwaipayan Deb"
__all__ = ["miescatter"]