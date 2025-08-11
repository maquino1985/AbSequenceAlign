"""
Domain layer for the antibody sequence analysis system.
This layer contains the core business logic and domain models.
"""

# Export value objects
    AnnotationMetadata,
)

# Export domain entities
    BiologicFeature,
)

# Export enums and domain services
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
