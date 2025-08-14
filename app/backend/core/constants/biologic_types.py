"""
Constants for biologic types.
"""

from enum import Enum


class BiologicType(str, Enum):
    """Types of biologics"""

    ANTIBODY = "antibody"
    PROTEIN = "protein"
    DNA = "dna"
    RNA = "rna"

