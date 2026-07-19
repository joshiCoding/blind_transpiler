"""
BlindTranspiler

A Python library for Universal Blind Quantum Computation and Quantum Homomorphic Encryption.
"""

__version__ = "1.0.0"

from .controllers.ubqc import BQC
from .controllers.qhe import bqc

__all__ = [
    "BQC",
    "bqc",
]

