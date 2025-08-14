"""
Constants for feature types.
"""

from enum import Enum


class FeatureType(str, Enum):
    """Types of antibody features"""

    GENE = "GENE"
    ALLELE = "ALLELE"
    ISOTYPE = "ISOTYPE"
    MUTATION = "MUTATION"
    POST_TRANSLATIONAL = "POST_TRANSLATIONAL"
    CDR1 = "CDR1"
    CDR2 = "CDR2"
    CDR3 = "CDR3"
    FR1 = "FR1"
    FR2 = "FR2"
    FR3 = "FR3"
    FR4 = "FR4"

