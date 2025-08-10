"""
Clean domain models for the antibody sequence analysis system.
These models represent the core business entities without infrastructure dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from ..core.exceptions import ValidationError, SequenceValidationError


# =============================================================================
# VALUE OBJECTS
# =============================================================================


@dataclass(frozen=True)
class AminoAcidSequence:
    """Value object representing an amino acid sequence"""

    sequence: str

    def __post_init__(self):
        if not self._is_valid_sequence():
            raise SequenceValidationError(
                f"Invalid amino acid sequence: {self.sequence}",
                field="sequence",
                value=self.sequence,
            )

    def _is_valid_sequence(self) -> bool:
        """Validate that the sequence contains only valid amino acids"""
        if not self.sequence or not isinstance(self.sequence, str):
            return False

        # Valid amino acid characters (including X for unknown)
        valid_chars = set("ACDEFGHIKLMNPQRSTVWYX")
        return all(char.upper() in valid_chars for char in self.sequence)

    def __len__(self) -> int:
        return len(self.sequence)

    def __str__(self) -> str:
        return self.sequence

    def upper(self) -> "AminoAcidSequence":
        """Return uppercase version of the sequence"""
        return AminoAcidSequence(self.sequence.upper())


@dataclass(frozen=True)
class SequencePosition:
    """Value object representing a position in a sequence"""

    position: int
    insertion: Optional[str] = None

    def __post_init__(self):
        if self.position < 0:
            raise ValidationError(
                f"Position must be non-negative, got: {self.position}",
                field="position",
                value=self.position,
            )

    def __str__(self) -> str:
        if self.insertion:
            return f"{self.position}{self.insertion}"
        return str(self.position)


@dataclass(frozen=True)
class RegionBoundary:
    """Value object representing the boundaries of a region"""

    start: int
    end: int

    def __post_init__(self):
        if self.start < 0 or self.end < 0:
            raise ValidationError(
                f"Boundaries must be non-negative: start={self.start}, end={self.end}",
                field="boundaries",
                value={"start": self.start, "end": self.end},
            )
        if self.start > self.end:
            raise ValidationError(
                f"Start position must be <= end position: start={self.start}, "
                f"end={self.end}",
                field="boundaries",
                value={"start": self.start, "end": self.end},
            )

    def contains(self, position: int) -> bool:
        """Check if a position is within this boundary"""
        return self.start <= position <= self.end

    def length(self) -> int:
        """Get the length of this region"""
        return self.end - self.start + 1


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


# =============================================================================
# DOMAIN ENTITIES
# =============================================================================


@dataclass
class AntibodyRegion:
    """Domain entity representing an antibody region (CDR, FR, etc.)"""

    name: str
    region_type: RegionType
    boundary: RegionBoundary
    sequence: AminoAcidSequence
    numbering_scheme: NumberingScheme

    def __post_init__(self):
        if not self.name:
            raise ValidationError("Region name cannot be empty", field="name")

        # Validate that sequence length matches boundary
        expected_length = self.boundary.length()
        actual_length = len(self.sequence)
        if expected_length != actual_length:
            raise ValidationError(
                f"Sequence length ({actual_length}) does not match boundary length "
                f"({expected_length})",
                field="sequence",
                value={
                    "sequence_length": actual_length,
                    "boundary_length": expected_length,
                },
            )

    @property
    def start(self) -> int:
        return self.boundary.start

    @property
    def end(self) -> int:
        return self.boundary.end

    @property
    def length(self) -> int:
        return self.boundary.length()

    def contains_position(self, position: int) -> bool:
        """Check if a position is within this region"""
        return self.boundary.contains(position)


@dataclass
class AntibodyDomain:
    """Domain entity representing an antibody domain (V, C, or linker)"""

    domain_type: DomainType
    sequence: AminoAcidSequence
    numbering_scheme: NumberingScheme
    regions: Dict[str, AntibodyRegion] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.domain_type:
            raise ValidationError(
                "Domain type cannot be empty", field="domain_type"
            )

        # Validate that all regions are within the domain sequence
        for region_name, region in self.regions.items():
            if region.end >= len(self.sequence):
                raise ValidationError(
                    f"Region '{region_name}' extends beyond domain sequence",
                    field="regions",
                    value={
                        "region": region_name,
                        "region_end": region.end,
                        "sequence_length": len(self.sequence),
                    },
                )

    def add_region(self, region: AntibodyRegion) -> None:
        """Add a region to this domain"""
        self.regions[region.name] = region

    def get_region(self, region_name: str) -> Optional[AntibodyRegion]:
        """Get a region by name"""
        return self.regions.get(region_name)

    def get_regions_by_type(
        self, region_type: RegionType
    ) -> List[AntibodyRegion]:
        """Get all regions of a specific type"""
        return [
            region
            for region in self.regions.values()
            if region.region_type == region_type
        ]

    @property
    def length(self) -> int:
        return len(self.sequence)


@dataclass
class AntibodyChain:
    """Domain entity representing an antibody chain"""

    name: str
    chain_type: ChainType
    sequence: AminoAcidSequence
    domains: List[AntibodyDomain] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            raise ValidationError("Chain name cannot be empty", field="name")

        # Validate that all domains are within the chain sequence
        total_domain_length = sum(
            len(domain.sequence) for domain in self.domains
        )
        if total_domain_length > len(self.sequence):
            raise ValidationError(
                f"Total domain length ({total_domain_length}) exceeds chain length "
                f"({len(self.sequence)})",
                field="domains",
                value={
                    "total_domain_length": total_domain_length,
                    "chain_length": len(self.sequence),
                },
            )

    def add_domain(self, domain: AntibodyDomain) -> None:
        """Add a domain to this chain"""
        self.domains.append(domain)

    def get_domains_by_type(
        self, domain_type: DomainType
    ) -> List[AntibodyDomain]:
        """Get all domains of a specific type"""
        return [
            domain
            for domain in self.domains
            if domain.domain_type == domain_type
        ]

    def get_variable_domain(self) -> Optional[AntibodyDomain]:
        """Get the variable domain (V) if it exists"""
        variable_domains = self.get_domains_by_type(DomainType.VARIABLE)
        return variable_domains[0] if variable_domains else None

    def get_constant_domain(self) -> Optional[AntibodyDomain]:
        """Get the constant domain (C) if it exists"""
        constant_domains = self.get_domains_by_type(DomainType.CONSTANT)
        return constant_domains[0] if constant_domains else None

    @property
    def length(self) -> int:
        return len(self.sequence)


@dataclass
class AntibodySequence:
    """Domain entity representing a complete antibody sequence"""

    name: str
    chains: List[AntibodyChain] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            raise ValidationError(
                "Sequence name cannot be empty", field="name"
            )

    def add_chain(self, chain: AntibodyChain) -> None:
        """Add a chain to this sequence"""
        self.chains.append(chain)

    def get_chain_by_type(
        self, chain_type: ChainType
    ) -> Optional[AntibodyChain]:
        """Get a chain by type"""
        for chain in self.chains:
            if chain.chain_type == chain_type:
                return chain
        return None

    def get_heavy_chain(self) -> Optional[AntibodyChain]:
        """Get the heavy chain if it exists"""
        return self.get_chain_by_type(ChainType.HEAVY)

    def get_light_chain(self) -> Optional[AntibodyChain]:
        """Get the light chain if it exists"""
        return self.get_chain_by_type(ChainType.LIGHT)

    @property
    def total_length(self) -> int:
        """Get the total length of all chains"""
        return sum(len(chain.sequence) for chain in self.chains)

    @property
    def chain_count(self) -> int:
        """Get the number of chains"""
        return len(self.chains)


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
