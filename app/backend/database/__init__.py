"""
Database module for AbSequenceAlign.
Provides SQLAlchemy setup, configuration, and base models.
"""

    get_engine_kwargs,
)
    get_db_session,
)
    UUIDv7,
)
    SequenceDomain,
    DomainFeature,
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
    # New biologic entity models
    "Biologic",
    "BiologicAlias",
    "Chain",
    "Sequence",
    "ChainSequence",
    "SequenceDomain",
    "DomainFeature",
]
