"""
Database module for AbSequenceAlign.
Provides SQLAlchemy setup, configuration, and base models.
"""

from .config import (
    DatabaseConfig,
    get_database_config,
    get_database_url,
    get_sync_database_url,
    get_engine_kwargs,
)
from .engine import (
    DatabaseEngine,
    get_database_engine,
    get_session,
    get_db_session,
)
from .base import (
    Base,
    BaseModel,
    TimestampMixin,
    UUIDMixin,
    SoftDeleteMixin,
    UUIDv7,
)
from .models import (
    # Lookup tables
    ChainType,
    DomainType,
    NumberingScheme,
    RegionType,
    FeatureType,
    JobType,
    JobStatus,
    # Main entity tables
    AntibodySequence,
    AntibodyChain,
    AntibodyDomain,
    AntibodyRegion,
    AntibodyFeature,
    ProcessingJob,
)

__all__ = [
    # Configuration
    "DatabaseConfig",
    "get_database_config",
    "get_database_url",
    "get_sync_database_url",
    "get_engine_kwargs",
    # Engine
    "DatabaseEngine",
    "get_database_engine",
    "get_session",
    "get_db_session",
    # Base models
    "Base",
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    "UUIDv7",
    # Lookup tables
    "ChainType",
    "DomainType",
    "NumberingScheme",
    "RegionType",
    "FeatureType",
    "JobType",
    "JobStatus",
    # Database models
    "AntibodySequence",
    "AntibodyChain",
    "AntibodyDomain",
    "AntibodyRegion",
    "AntibodyFeature",
    "ProcessingJob",
]
