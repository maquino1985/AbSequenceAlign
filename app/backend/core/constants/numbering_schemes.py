"""
Constants for numbering schemes.
"""

from enum import Enum


class NumberingScheme(str, Enum):
    """Antibody numbering schemes"""

    IMGT = "imgt"
    KABAT = "kabat"
    CHOTHIA = "chothia"
    MARTIN = "martin"
    AHO = "aho"
    CGG = "cgg"

