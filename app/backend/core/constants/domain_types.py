"""
Constants for domain types.
"""

from enum import Enum


class DomainType(str, Enum):
    """Types of antibody domains"""

    VARIABLE = "V"
    CONSTANT = "C"
    LINKER = "LINKER"


class RegionType(str, Enum):
    """Types of antibody regions"""

    CDR1 = "CDR1"
    CDR2 = "CDR2"
    CDR3 = "CDR3"
    FR1 = "FR1"
    FR2 = "FR2"
    FR3 = "FR3"
    FR4 = "FR4"
    CONSTANT = "CONSTANT"
    LINKER = "LINKER"

