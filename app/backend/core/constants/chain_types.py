"""
Constants for chain types.
"""

from enum import Enum


class ChainType(str, Enum):
    """Types of antibody chains"""

    HEAVY = "HEAVY"
    LIGHT = "LIGHT"
    KAPPA = "KAPPA"
    LAMBDA = "LAMBDA"
    BETA = "BETA"
    GAMMA = "GAMMA"
    DELTA = "DELTA"
    EPSILON = "EPSILON"
    ZETA = "ZETA"
    ALPHA = "ALPHA"
    THETA = "THETA"
    IOTA = "IOTA"
    UNKNOWN = "UNKNOWN"

