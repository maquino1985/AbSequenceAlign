"""
Domain entities for the antibody sequence analysis system.
Entities have identity and lifecycle, and contain business logic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.domain.entities import AntibodyFeature
from abc import ABC, abstractmethod

from backend.domain.value_objects import (
    AminoAcidSequence,
    RegionBoundary,
    SequenceIdentifier,
    ConfidenceScore,
    AnnotationMetadata,
)
from backend.domain.models import (
    ChainType,
    DomainType,
    RegionType,
    NumberingScheme,
    FeatureType,
)
from backend.core.exceptions import ValidationError, DomainError


class DomainEntity(ABC):
    """Abstract base class for all domain entities"""

    @property
    @abstractmethod
    def id(self) -> str:
        """Get the unique identifier for this entity"""
        pass

    def __eq__(self, other: object) -> bool:
        """Check if two entities are equal based on their ID"""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on entity ID"""
        return hash(self.id)


# =============================================================================
# NEW BIOLOGIC DOMAIN ENTITIES
# =============================================================================


@dataclass
class BiologicEntity(DomainEntity):
    """Domain entity representing any biologic (antibodies, enzymes, receptors, etc.)"""

    name: str
    description: Optional[str] = None
    organism: Optional[str] = None
    biologic_type: str = "antibody"  # antibody, protein, dna, rna
    chains: List["BiologicChain"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            raise ValidationError(
                "Biologic name cannot be empty", field="name"
            )

    @property
    def id(self) -> str:
        """Get unique identifier for this biologic"""
        return f"{self.name}_{self.biologic_type}_{len(self.chains)}_chains"

    def add_chain(self, chain: "BiologicChain") -> None:
        """Add a chain to this biologic"""
        self.chains.append(chain)

    def get_chain_by_name(self, name: str) -> Optional["BiologicChain"]:
        """Get a chain by name"""
        for chain in self.chains:
            if chain.name == name:
                return chain
        return None

    def get_chains_by_type(self, chain_type: str) -> List["BiologicChain"]:
        """Get all chains of a specific type"""
        return [
            chain for chain in self.chains if chain.chain_type == chain_type
        ]

    @property
    def total_length(self) -> int:
        """Get the total length of all chains"""
        return sum(chain.length for chain in self.chains)

    @property
    def chain_count(self) -> int:
        """Get the number of chains"""
        return len(self.chains)

    def is_antibody(self) -> bool:
        """Check if this is an antibody"""
        return self.biologic_type.lower() == "antibody"

    def is_protein(self) -> bool:
        """Check if this is a protein"""
        return self.biologic_type.lower() == "protein"

    def is_dna(self) -> bool:
        """Check if this is DNA"""
        return self.biologic_type.lower() == "dna"

    def is_rna(self) -> bool:
        """Check if this is RNA"""
        return self.biologic_type.lower() == "rna"


@dataclass
class BiologicChain(DomainEntity):
    """Domain entity representing a chain within a biologic"""

    name: str
    chain_type: str  # HEAVY, LIGHT, SINGLE_CHAIN, etc.
    sequences: List["BiologicSequence"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            raise ValidationError("Chain name cannot be empty", field="name")

    @property
    def id(self) -> str:
        """Get unique identifier for this chain"""
        return f"{self.name}_{self.chain_type}_{len(self.sequences)}_sequences"

    def add_sequence(self, sequence: "BiologicSequence") -> None:
        """Add a sequence to this chain"""
        self.sequences.append(sequence)

    def get_sequence_by_type(
        self, sequence_type: str
    ) -> Optional["BiologicSequence"]:
        """Get a sequence by type"""
        for sequence in self.sequences:
            if sequence.sequence_type == sequence_type:
                return sequence
        return None

    @property
    def length(self) -> int:
        """Get the total length of all sequences"""
        return sum(len(sequence.sequence_data) for sequence in self.sequences)

    def is_heavy_chain(self) -> bool:
        """Check if this is a heavy chain"""
        return self.chain_type.upper() == "HEAVY"

    def is_light_chain(self) -> bool:
        """Check if this is a light chain"""
        return self.chain_type.upper() in ["LIGHT", "KAPPA", "LAMBDA"]


@dataclass
class BiologicSequence(DomainEntity):
    """Domain entity representing a sequence (protein, DNA, RNA)"""

    sequence_type: str  # PROTEIN, DNA, RNA
    sequence_data: str
    description: Optional[str] = None
    domains: List["BiologicDomain"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.sequence_data:
            raise ValidationError(
                "Sequence data cannot be empty", field="sequence_data"
            )

    @property
    def id(self) -> str:
        """Get unique identifier for this sequence"""
        return f"{self.sequence_type}_{len(self.sequence_data)}_{hash(self.sequence_data)}"

    @property
    def length(self) -> int:
        """Get the length of the sequence"""
        return len(self.sequence_data)

    def add_domain(self, domain: "BiologicDomain") -> None:
        """Add a domain to this sequence"""
        self.domains.append(domain)

    def get_domains_by_type(self, domain_type: str) -> List["BiologicDomain"]:
        """Get all domains of a specific type"""
        return [
            domain
            for domain in self.domains
            if domain.domain_type == domain_type
        ]

    def is_protein(self) -> bool:
        """Check if this is a protein sequence"""
        return self.sequence_type.upper() == "PROTEIN"

    def is_dna(self) -> bool:
        """Check if this is a DNA sequence"""
        return self.sequence_type.upper() == "DNA"

    def is_rna(self) -> bool:
        """Check if this is an RNA sequence"""
        return self.sequence_type.upper() == "RNA"


@dataclass
class BiologicDomain(DomainEntity):
    """Domain entity representing a domain within a sequence"""

    domain_type: str  # VARIABLE, CONSTANT, LINKER, etc.
    start_position: int
    end_position: int
    confidence_score: Optional[int] = None  # 0-100
    features: List["BiologicFeature"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.start_position < 0:
            raise ValidationError(
                "Start position cannot be negative", field="start_position"
            )
        if self.end_position < self.start_position:
            raise ValidationError(
                "End position must be >= start position", field="end_position"
            )

    @property
    def id(self) -> str:
        """Get unique identifier for this domain"""
        return f"{self.domain_type}_{self.start_position}_{self.end_position}"

    @property
    def length(self) -> int:
        """Get the length of this domain"""
        return self.end_position - self.start_position + 1

    def add_feature(self, feature: "BiologicFeature") -> None:
        """Add a feature to this domain"""
        self.features.append(feature)

    def get_features_by_type(
        self, feature_type: str
    ) -> List["BiologicFeature"]:
        """Get all features of a specific type"""
        return [
            feature
            for feature in self.features
            if feature.feature_type == feature_type
        ]

    def contains_position(self, position: int) -> bool:
        """Check if a position is within this domain"""
        return self.start_position <= position <= self.end_position

    def overlaps_with(self, other: "BiologicDomain") -> bool:
        """Check if this domain overlaps with another"""
        return not (
            self.end_position < other.start_position
            or other.end_position < self.start_position
        )

    def is_variable_domain(self) -> bool:
        """Check if this is a variable domain"""
        return self.domain_type.upper() == "VARIABLE"

    def is_constant_domain(self) -> bool:
        """Check if this is a constant domain"""
        return self.domain_type.upper() == "CONSTANT"

    def is_linker_domain(self) -> bool:
        """Check if this is a linker domain"""
        return self.domain_type.upper() == "LINKER"


@dataclass
class BiologicFeature(DomainEntity):
    """Domain entity representing a feature within a domain"""

    feature_type: str  # CDR, FR, MUTATION, etc.
    name: str
    value: str
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    confidence_score: Optional[int] = None  # 0-100
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.name:
            raise ValidationError("Feature name cannot be empty", field="name")
        if not self.value:
            raise ValidationError(
                "Feature value cannot be empty", field="value"
            )

    @property
    def id(self) -> str:
        """Get unique identifier for this feature"""
        position_str = (
            f"_{self.start_position}_{self.end_position}"
            if self.start_position is not None
            else ""
        )
        return f"{self.name}_{self.feature_type}{position_str}"

    def is_cdr_region(self) -> bool:
        """Check if this is a CDR region"""
        return self.feature_type.upper() in ["CDR1", "CDR2", "CDR3"]

    def is_fr_region(self) -> bool:
        """Check if this is an FR region"""
        return self.feature_type.upper() in ["FR1", "FR2", "FR3", "FR4"]

    def is_mutation(self) -> bool:
        """Check if this is a mutation feature"""
        return self.feature_type.upper() == "MUTATION"

    def has_high_confidence(self, threshold: int = 80) -> bool:
        """Check if the feature has high confidence"""
        if self.confidence_score is None:
            return False
        return self.confidence_score >= threshold
