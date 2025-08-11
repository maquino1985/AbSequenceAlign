"""
Domain models for the antibody sequence analysis system.
This file contains enums and domain services.
Value objects and entities are in separate files.
"""

from enum import Enum

from backend.domain.value_objects import RegionBoundary


# =============================================================================
# VALUE OBJECTS
# =============================================================================

# Value objects have been moved to value_objects.py


# =============================================================================
# ENUMERATIONS
# =============================================================================


class ChainType(str, Enum):
    """Types of antibody chains"""

    HEAVY = "H"
    LIGHT = "L"
    KAPPA = "K"
    LAMBDA = "L"
    BETA = "B"
    GAMMA = "G"
    DELTA = "D"
    EPSILON = "E"
    ZETA = "Z"
    ALPHA = "A"
    THETA = "T"
    IOTA = "I"


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


class NumberingScheme(str, Enum):
    """Antibody numbering schemes"""

    IMGT = "imgt"
    KABAT = "kabat"
    CHOTHIA = "chothia"
    MARTIN = "martin"
    AHO = "aho"
    CGG = "cgg"


class FeatureType(str, Enum):
    """Types of antibody features"""

    GENE = "GENE"
    ALLELE = "ALLELE"
    ISOTYPE = "ISOTYPE"
    MUTATION = "MUTATION"
    POST_TRANSLATIONAL = "POST_TRANSLATIONAL"


# =============================================================================
# DOMAIN ENTITIES
# =============================================================================

# Domain entities have been moved to entities.py


# =============================================================================
# DOMAIN SERVICES
# =============================================================================


class SequenceValidator:
    """Domain service for validating sequences"""

    @staticmethod
    def validate_amino_acid_sequence(sequence: str) -> bool:
        """Validate that a sequence contains only valid amino acids"""
        if not sequence or not isinstance(sequence, str):
            return False

        valid_chars = set("ACDEFGHIKLMNPQRSTVWYX")
        return all(char.upper() in valid_chars for char in sequence)

    @staticmethod
    def validate_sequence_length(
        sequence: str, min_length: int = 1, max_length: int = 10000
    ) -> bool:
        """Validate sequence length"""
        if not sequence:
            return False

        length = len(sequence)
        return min_length <= length <= max_length

    @staticmethod
    def validate_chain_type(chain_type: str) -> bool:
        """Validate chain type"""
        try:
            ChainType(chain_type)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_domain_type(domain_type: str) -> bool:
        """Validate domain type"""
        try:
            DomainType(domain_type)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_protein_sequence(sequence: str) -> bool:
        """Check if a sequence is a valid protein sequence"""
        return SequenceValidator.validate_amino_acid_sequence(sequence)

    @staticmethod
    def is_valid_dna_sequence(sequence: str) -> bool:
        """Check if a sequence is a valid DNA sequence"""
        if not sequence or not isinstance(sequence, str):
            return False

        valid_chars = set("ACGTN")
        return all(char.upper() in valid_chars for char in sequence)


class RegionCalculator:
    """Domain service for calculating region boundaries and properties"""

    @staticmethod
    def calculate_region_boundary(start: int, end: int) -> RegionBoundary:
        """Calculate a region boundary"""
        return RegionBoundary(start, end)

    @staticmethod
    def extract_region_sequence(
        sequence: str, boundary: RegionBoundary
    ) -> str:
        """Extract a region sequence from a larger sequence"""
        return sequence[boundary.start : boundary.end + 1]

    @staticmethod
    def calculate_region_overlap(
        boundary1: RegionBoundary, boundary2: RegionBoundary
    ) -> int:
        """Calculate the overlap between two region boundaries"""
        overlap_start = max(boundary1.start, boundary2.start)
        overlap_end = min(boundary1.end, boundary2.end)
        return max(0, overlap_end - overlap_start + 1)

    @staticmethod
    def regions_are_adjacent(
        boundary1: RegionBoundary, boundary2: RegionBoundary
    ) -> bool:
        """Check if two regions are adjacent"""
        return (
            boundary1.end + 1 == boundary2.start
            or boundary2.end + 1 == boundary1.start
        )

    @staticmethod
    def calculate_boundary(
        start: int, end: int, sequence_length: int
    ) -> RegionBoundary:
        """Calculate a region boundary with validation"""
        if start < 0 or end >= sequence_length or start > end:
            raise ValueError(
                f"Invalid boundary: start={start}, end={end}, length={sequence_length}"
            )
        return RegionBoundary(start, end)
