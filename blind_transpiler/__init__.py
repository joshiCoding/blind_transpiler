"""
BlindTranspiler

A Python library for Universal Blind Quantum Computation and Quantum Homomorphic Encryption.
"""

__version__ = "1.0.0"

from .controllers.orchestrator import BQC, bqc

__all__ = [
    "BQC",
    "bqc",
]

