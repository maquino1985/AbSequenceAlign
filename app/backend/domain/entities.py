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


@dataclass
class AntibodyRegion(DomainEntity):
    """Domain entity representing an antibody region (CDR, FR, etc.)"""

    name: str
    region_type: RegionType
    boundary: RegionBoundary
    sequence: AminoAcidSequence
    numbering_scheme: NumberingScheme
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: Optional[ConfidenceScore] = None

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
    def id(self) -> str:
        """Get unique identifier for this region"""
        return f"{self.name}_{self.region_type}_{self.boundary.start}_{self.boundary.end}"

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

    def overlaps_with(self, other: "AntibodyRegion") -> bool:
        """Check if this region overlaps with another"""
        return self.boundary.overlaps_with(other.boundary)

    def is_adjacent_to(self, other: "AntibodyRegion") -> bool:
        """Check if this region is adjacent to another"""
        return self.boundary.is_adjacent_to(other.boundary)

    def get_sequence_fragment(self) -> AminoAcidSequence:
        """Get the sequence fragment for this region"""
        return self.sequence.substring(self.start, self.end + 1)

    def is_cdr_region(self) -> bool:
        """Check if this is a CDR region"""
        return self.region_type in [
            RegionType.CDR1,
            RegionType.CDR2,
            RegionType.CDR3,
        ]

    def is_fr_region(self) -> bool:
        """Check if this is an FR region"""
        return self.region_type in [
            RegionType.FR1,
            RegionType.FR2,
            RegionType.FR3,
            RegionType.FR4,
        ]

    def has_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the annotation has high confidence"""
        if not self.confidence_score:
            return False
        return self.confidence_score.is_high_confidence(threshold)

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to this region"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None):
        """Get metadata value"""
        return self.metadata.get(key, default)


@dataclass
class AntibodyDomain(DomainEntity):
    """Domain entity representing an antibody domain (V, C, or linker)"""

    domain_type: DomainType
    sequence: AminoAcidSequence
    numbering_scheme: NumberingScheme
    regions: Dict[str, AntibodyRegion] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    annotation_metadata: Optional[AnnotationMetadata] = None

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

    @property
    def id(self) -> str:
        """Get unique identifier for this domain"""
        return f"{self.domain_type}_{len(self.sequence)}_{hash(self.sequence)}"

    def add_region(self, region: AntibodyRegion) -> None:
        """Add a region to this domain"""
        # Validate region is within domain bounds
        if region.end >= len(self.sequence):
            raise ValidationError(
                f"Region '{region.name}' extends beyond domain sequence",
                field="region",
                value={
                    "region_end": region.end,
                    "sequence_length": len(self.sequence),
                },
            )

        # Check for overlapping regions
        for existing_region in self.regions.values():
            if region.overlaps_with(existing_region):
                raise DomainError(
                    f"Region '{region.name}' overlaps with existing region '{existing_region.name}'"
                )

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

    def get_cdr_regions(self) -> List[AntibodyRegion]:
        """Get all CDR regions"""
        return [
            region
            for region in self.regions.values()
            if region.is_cdr_region()
        ]

    def get_fr_regions(self) -> List[AntibodyRegion]:
        """Get all FR regions"""
        return [
            region for region in self.regions.values() if region.is_fr_region()
        ]

    def has_region(self, region_name: str) -> bool:
        """Check if domain has a specific region"""
        return region_name in self.regions

    def remove_region(self, region_name: str) -> None:
        """Remove a region from this domain"""
        if region_name in self.regions:
            del self.regions[region_name]

    def get_region_boundaries(self) -> List[RegionBoundary]:
        """Get all region boundaries in this domain"""
        return [region.boundary for region in self.regions.values()]

    def get_covered_positions(self) -> Set[int]:
        """Get all positions covered by regions in this domain"""
        covered = set()
        for region in self.regions.values():
            covered.update(range(region.start, region.end + 1))
        return covered

    def get_uncovered_positions(self) -> Set[int]:
        """Get all positions not covered by regions in this domain"""
        all_positions = set(range(len(self.sequence)))
        covered_positions = self.get_covered_positions()
        return all_positions - covered_positions

    @property
    def length(self) -> int:
        return len(self.sequence)

    def is_variable_domain(self) -> bool:
        """Check if this is a variable domain"""
        return self.domain_type == DomainType.VARIABLE

    def is_constant_domain(self) -> bool:
        """Check if this is a constant domain"""
        return self.domain_type == DomainType.CONSTANT

    def is_linker_domain(self) -> bool:
        """Check if this is a linker domain"""
        return self.domain_type == DomainType.LINKER


@dataclass
class AntibodyChain(DomainEntity):
    """Domain entity representing an antibody chain"""

    name: str
    chain_type: ChainType
    sequence: AminoAcidSequence
    domains: List[AntibodyDomain] = field(default_factory=list)
    features: List["AntibodyFeature"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    sequence_id: Optional[SequenceIdentifier] = None

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

    @property
    def id(self) -> str:
        """Get unique identifier for this chain"""
        if self.sequence_id:
            return str(self.sequence_id)
        return f"{self.name}_{self.chain_type}_{len(self.sequence)}"

    def add_domain(self, domain: AntibodyDomain) -> None:
        """Add a domain to this chain"""
        # Validate domain sequence is part of chain sequence
        if str(domain.sequence) not in str(self.sequence):
            raise ValidationError(
                "Domain sequence is not part of chain sequence",
                field="domain",
                value={
                    "domain_sequence": str(domain.sequence),
                    "chain_sequence": str(self.sequence),
                },
            )

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

    def get_linker_domains(self) -> List[AntibodyDomain]:
        """Get all linker domains"""
        return self.get_domains_by_type(DomainType.LINKER)

    def has_variable_domain(self) -> bool:
        """Check if chain has a variable domain"""
        return self.get_variable_domain() is not None

    def has_constant_domain(self) -> bool:
        """Check if chain has a constant domain"""
        return self.get_constant_domain() is not None

    def is_heavy_chain(self) -> bool:
        """Check if this is a heavy chain"""
        return self.chain_type == ChainType.HEAVY

    def is_light_chain(self) -> bool:
        """Check if this is a light chain"""
        return self.chain_type in [
            ChainType.LIGHT,
            ChainType.KAPPA,
            ChainType.LAMBDA,
        ]

    def get_all_regions(self) -> List[AntibodyRegion]:
        """Get all regions from all domains in this chain"""
        regions = []
        for domain in self.domains:
            regions.extend(domain.regions.values())
        return regions

    def get_regions_by_type(
        self, region_type: RegionType
    ) -> List[AntibodyRegion]:
        """Get all regions of a specific type from all domains"""
        return [
            region
            for region in self.get_all_regions()
            if region.region_type == region_type
        ]

    def add_feature(self, feature: "AntibodyFeature") -> None:
        """Add a feature to this chain"""
        self.features.append(feature)

    def get_features_by_type(
        self, feature_type: FeatureType
    ) -> List["AntibodyFeature"]:
        """Get all features of a specific type"""
        return [
            feature
            for feature in self.features
            if feature.feature_type == feature_type
        ]

    def get_mutations(self) -> List["AntibodyFeature"]:
        """Get all mutation features"""
        return self.get_features_by_type(FeatureType.MUTATION)

    def get_post_translational_modifications(self) -> List["AntibodyFeature"]:
        """Get all post-translational modification features"""
        return self.get_features_by_type(FeatureType.POST_TRANSLATIONAL)

    def get_gene_features(self) -> List["AntibodyFeature"]:
        """Get all gene-related features"""
        return [
            feature for feature in self.features if feature.is_gene_related()
        ]

    @property
    def length(self) -> int:
        return len(self.sequence)


@dataclass
class AntibodySequence(DomainEntity):
    """Domain entity representing a complete antibody sequence"""

    name: str
    chains: List[AntibodyChain] = field(default_factory=list)
    features: List["AntibodyFeature"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    sequence_id: Optional[SequenceIdentifier] = None

    def __post_init__(self):
        if not self.name:
            raise ValidationError(
                "Sequence name cannot be empty", field="name"
            )

    @property
    def id(self) -> str:
        """Get unique identifier for this sequence"""
        if self.sequence_id:
            return str(self.sequence_id)
        return f"{self.name}_{len(self.chains)}_chains"

    def add_chain(self, chain: AntibodyChain) -> None:
        """Add a chain to this sequence"""
        # Check for duplicate chain types
        existing_chain_types = {c.chain_type for c in self.chains}
        if chain.chain_type in existing_chain_types:
            raise DomainError(
                f"Chain type {chain.chain_type} already exists in sequence"
            )

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
        light_chains = [
            chain for chain in self.chains if chain.is_light_chain()
        ]
        return light_chains[0] if light_chains else None

    def has_heavy_chain(self) -> bool:
        """Check if sequence has a heavy chain"""
        return self.get_heavy_chain() is not None

    def has_light_chain(self) -> bool:
        """Check if sequence has a light chain"""
        return self.get_light_chain() is not None

    def is_complete_antibody(self) -> bool:
        """Check if this is a complete antibody with both heavy and light chains"""
        return self.has_heavy_chain() and self.has_light_chain()

    def is_scfv(self) -> bool:
        """Check if this is a single-chain variable fragment (scFv)"""
        return (
            len(self.chains) == 1
            and self.chains[0].has_variable_domain()
            and self.chains[0].get_linker_domains()
        )

    def get_all_domains(self) -> List[AntibodyDomain]:
        """Get all domains from all chains"""
        domains = []
        for chain in self.chains:
            domains.extend(chain.domains)
        return domains

    def get_domains_by_type(
        self, domain_type: DomainType
    ) -> List[AntibodyDomain]:
        """Get all domains of a specific type from all chains"""
        return [
            domain
            for domain in self.get_all_domains()
            if domain.domain_type == domain_type
        ]

    def get_all_regions(self) -> List[AntibodyRegion]:
        """Get all regions from all domains in all chains"""
        regions = []
        for chain in self.chains:
            regions.extend(chain.get_all_regions())
        return regions

    def get_regions_by_type(
        self, region_type: RegionType
    ) -> List[AntibodyRegion]:
        """Get all regions of a specific type from all chains"""
        return [
            region
            for region in self.get_all_regions()
            if region.region_type == region_type
        ]

    def add_feature(self, feature: "AntibodyFeature") -> None:
        """Add a feature to this sequence"""
        self.features.append(feature)

    def get_features_by_type(
        self, feature_type: FeatureType
    ) -> List["AntibodyFeature"]:
        """Get all features of a specific type"""
        return [
            feature
            for feature in self.features
            if feature.feature_type == feature_type
        ]

    def get_all_features(self) -> List["AntibodyFeature"]:
        """Get all features from all chains and sequence level"""
        all_features = self.features.copy()
        for chain in self.chains:
            all_features.extend(chain.features)
        return all_features

    def get_mutations(self) -> List["AntibodyFeature"]:
        """Get all mutation features"""
        return self.get_features_by_type(FeatureType.MUTATION)

    def get_post_translational_modifications(self) -> List["AntibodyFeature"]:
        """Get all post-translational modification features"""
        return self.get_features_by_type(FeatureType.POST_TRANSLATIONAL)

    def get_gene_features(self) -> List["AntibodyFeature"]:
        """Get all gene-related features"""
        return [
            feature for feature in self.features if feature.is_gene_related()
        ]

    @property
    def total_length(self) -> int:
        """Get the total length of all chains"""
        return sum(len(chain.sequence) for chain in self.chains)

    @property
    def chain_count(self) -> int:
        """Get the number of chains"""
        return len(self.chains)


@dataclass
class AntibodyFeature(DomainEntity):
    """Domain entity representing an antibody feature (mutation, modification, etc.)"""

    name: str
    feature_type: FeatureType
    value: str
    boundary: Optional[RegionBoundary] = None
    confidence_score: Optional[ConfidenceScore] = None
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
        boundary_str = (
            f"_{self.boundary.start}_{self.boundary.end}"
            if self.boundary
            else ""
        )
        return f"{self.name}_{self.feature_type}{boundary_str}"

    @property
    def start(self) -> Optional[int]:
        """Get the start position of this feature"""
        return self.boundary.start if self.boundary else None

    @property
    def end(self) -> Optional[int]:
        """Get the end position of this feature"""
        return self.boundary.end if self.boundary else None

    @property
    def length(self) -> Optional[int]:
        """Get the length of this feature"""
        return self.boundary.length() if self.boundary else None

    def has_position(self, position: int) -> bool:
        """Check if a position is within this feature"""
        if not self.boundary:
            return False
        return self.boundary.contains(position)

    def overlaps_with(self, other: "AntibodyFeature") -> bool:
        """Check if this feature overlaps with another"""
        if not self.boundary or not other.boundary:
            return False
        return self.boundary.overlaps_with(other.boundary)

    def is_adjacent_to(self, other: "AntibodyFeature") -> bool:
        """Check if this feature is adjacent to another"""
        if not self.boundary or not other.boundary:
            return False
        return self.boundary.is_adjacent_to(other.boundary)

    def is_mutation(self) -> bool:
        """Check if this is a mutation feature"""
        return self.feature_type == FeatureType.MUTATION

    def is_post_translational(self) -> bool:
        """Check if this is a post-translational modification"""
        return self.feature_type == FeatureType.POST_TRANSLATIONAL

    def is_gene_related(self) -> bool:
        """Check if this is a gene-related feature"""
        return self.feature_type in [FeatureType.GENE, FeatureType.ALLELE]

    def has_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if the feature has high confidence"""
        if not self.confidence_score:
            return False
        return self.confidence_score.is_high_confidence(threshold)

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to this feature"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default=None):
        """Get metadata value"""
        return self.metadata.get(key, default)
