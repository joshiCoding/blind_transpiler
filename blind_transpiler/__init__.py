"""
BlindTranspiler

A Python library for Universal Blind Quantum Computation and Quantum Homomorphic Encryption.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("blind-transpiler")
except PackageNotFoundError:
    __version__ = "unknown"
    
from .controllers.orchestrator import BQC, bqc

__all__ = [
    "BQC",
    "bqc",
]


