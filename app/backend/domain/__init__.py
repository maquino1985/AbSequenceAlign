"""
Domain layer for the antibody sequence analysis system.
This layer contains the core business logic and domain models.
"""

# Export value objects
from .value_objects import (
    AminoAcidSequence,
    SequencePosition,
    RegionBoundary,
    SequenceIdentifier,
    ConfidenceScore,
    AnnotationMetadata,
)

# Export domain entities
from .entities import (
    DomainEntity,
    AntibodyRegion,
    AntibodyDomain,
    AntibodyChain,
    AntibodySequence,
)

# Export enums and domain services
from .models import (
    ChainType,
    DomainType,
    RegionType,
    NumberingScheme,
    SequenceValidator,
    RegionCalculator,
)

__all__ = [
    # Value objects
    "AminoAcidSequence",
    "SequencePosition",
    "RegionBoundary",
    "SequenceIdentifier",
    "ConfidenceScore",
    "AnnotationMetadata",
    # Domain entities
    "DomainEntity",
    "AntibodyRegion",
    "AntibodyDomain",
    "AntibodyChain",
    "AntibodySequence",
    # Enums and services
    "ChainType",
    "DomainType",
    "RegionType",
    "NumberingScheme",
    "SequenceValidator",
    "RegionCalculator",
]
