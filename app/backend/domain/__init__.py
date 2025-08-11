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
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
    BiologicDomain,
    BiologicFeature,
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
    "BiologicEntity",
    "BiologicChain",
    "BiologicSequence",
    "BiologicDomain",
    "BiologicFeature",
    # Enums and services
    "ChainType",
    "DomainType",
    "RegionType",
    "NumberingScheme",
    "SequenceValidator",
    "RegionCalculator",
]
