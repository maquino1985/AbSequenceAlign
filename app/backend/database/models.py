"""
SQLAlchemy models for AbSequenceAlign database.

This module contains the new biologic entity models for the refactored database schema.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base, UUIDv7


# =============================================================================
# New Biologic Entity Models
# =============================================================================


class Biologic(Base):
    """Main entity representing any biologic (antibodies, enzymes, receptors, etc.)"""

    __tablename__ = "biologics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    organism = Column(String(100), nullable=True, index=True)
    biologic_type = Column(
        String(50), nullable=False, default="antibody"
    )  # antibody, enzyme, receptor, etc.
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    aliases = relationship(
        "BiologicAlias",
        back_populates="biologic",
        cascade="all, delete-orphan",
    )
    chains = relationship(
        "Chain", back_populates="biologic", cascade="all, delete-orphan"
    )


class BiologicAlias(Base):
    """Multiple names/aliases for a biologic entity"""

    __tablename__ = "biologic_aliases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    biologic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("biologics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alias = Column(String(255), nullable=False, index=True)
    alias_type = Column(
        String(50), nullable=False
    )  # common_name, scientific_name, trade_name, etc.
    is_primary = Column(Boolean, default=False)
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    biologic = relationship("Biologic", back_populates="aliases")


class Chain(Base):
    """Chains within a biologic entity"""

    __tablename__ = "chains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    biologic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("biologics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)
    chain_type = Column(
        String(50), nullable=False
    )  # HEAVY, LIGHT, SINGLE_CHAIN, etc.
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    biologic = relationship("Biologic", back_populates="chains")
    sequences = relationship(
        "ChainSequence", back_populates="chain", cascade="all, delete-orphan"
    )


class Sequence(Base):
    """Generic sequence storage supporting protein, DNA, and RNA sequences"""

    __tablename__ = "sequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    sequence_type = Column(String(20), nullable=False)  # PROTEIN, DNA, RNA
    sequence_data = Column(Text, nullable=False)
    length = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    chain_sequences = relationship(
        "ChainSequence",
        back_populates="sequence",
        cascade="all, delete-orphan",
    )


class ChainSequence(Base):
    """Links chains to their sequences with positional information"""

    __tablename__ = "chain_sequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    chain_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sequences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    chain = relationship("Chain", back_populates="sequences")
    sequence = relationship("Sequence", back_populates="chain_sequences")
    domains = relationship(
        "SequenceDomain",
        back_populates="chain_sequence",
        cascade="all, delete-orphan",
    )


class SequenceDomain(Base):
    """Domains within sequences (e.g., variable, constant, linker domains)"""

    __tablename__ = "sequence_domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    chain_sequence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chain_sequences.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain_type = Column(
        String(50), nullable=False
    )  # VARIABLE, CONSTANT, LINKER, etc.
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    
    # Species and germline information
    species = Column(String(50), nullable=True, index=True)  # e.g., "human", "mouse", "rat"
    germline = Column(String(100), nullable=True, index=True)  # e.g., "IGHV1-2*02", "IGHG1*01"
    
    confidence_score = Column(Integer, nullable=True)  # 0-100
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    chain_sequence = relationship("ChainSequence", back_populates="domains")
    features = relationship(
        "DomainFeature",
        back_populates="sequence_domain",
        cascade="all, delete-orphan",
    )


class DomainFeature(Base):
    """Features within domains (e.g., CDR regions, FR regions, mutations)"""

    __tablename__ = "domain_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())
    sequence_domain_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sequence_domains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_type = Column(
        String(50), nullable=False
    )  # CDR, FR, MUTATION, etc.
    name = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    metadata_json = Column(JSONB, nullable=True, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    sequence_domain = relationship("SequenceDomain", back_populates="features")
