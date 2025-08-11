"""
SQLAlchemy models for AbSequenceAlign database.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


# Lookup Tables
class ChainType(Base):
    """Chain type lookup table."""

    __tablename__ = "chain_types"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "HEAVY", "LIGHT", "SINGLE_CHAIN"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Heavy Chain", "Light Chain", "Single Chain"
    description = Column(Text, nullable=True)

    # Relationships
    chains = relationship("AntibodyChain", back_populates="chain_type_ref")

    # Audit fields inherited from Base


class DomainType(Base):
    """Domain type lookup table."""

    __tablename__ = "domain_types"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "VARIABLE", "CONSTANT", "JOINING"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Variable Domain", "Constant Domain", "Joining Region"
    description = Column(Text, nullable=True)

    # Relationships
    domains = relationship("AntibodyDomain", back_populates="domain_type_ref")

    # Audit fields inherited from Base


class NumberingScheme(Base):
    """Numbering scheme lookup table."""

    __tablename__ = "numbering_schemes"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "IMGT", "KABAT", "CHOTHIA"
    name = Column(
        String(100), nullable=False
    )  # e.g., "IMGT Numbering", "Kabat Numbering", "Chothia Numbering"
    description = Column(Text, nullable=True)

    # Relationships
    chains = relationship(
        "AntibodyChain", back_populates="numbering_scheme_ref"
    )
    regions = relationship(
        "AntibodyRegion", back_populates="numbering_scheme_ref"
    )

    # Audit fields inherited from Base


class RegionType(Base):
    """Region type lookup table."""

    __tablename__ = "region_types"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "FR1", "CDR1", "FR2", "CDR2", "FR3", "CDR3", "FR4"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Framework Region 1", "Complementarity-Determining Region 1"
    description = Column(Text, nullable=True)

    # Relationships
    regions = relationship("AntibodyRegion", back_populates="region_type_ref")

    # Audit fields inherited from Base


class FeatureType(Base):
    """Feature type lookup table."""

    __tablename__ = "feature_types"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "GENE", "ALLELE", "ISOTYPE", "MUTATION", "POST_TRANSLATIONAL"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Gene", "Allele", "Isotype", "Mutation", "Post-Translational Modification"
    description = Column(Text, nullable=True)

    # Relationships
    features = relationship(
        "AntibodyFeature", back_populates="feature_type_ref"
    )

    # Audit fields inherited from Base


class JobType(Base):
    """Job type lookup table."""

    __tablename__ = "job_types"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "ANNOTATION", "ALIGNMENT", "ANALYSIS"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Sequence Annotation", "Sequence Alignment", "Sequence Analysis"
    description = Column(Text, nullable=True)

    # Relationships
    jobs = relationship("ProcessingJob", back_populates="job_type_ref")

    # Audit fields inherited from Base


class JobStatus(Base):
    """Job status lookup table."""

    __tablename__ = "job_statuses"

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Pending", "Running", "Completed", "Failed", "Cancelled"
    description = Column(Text, nullable=True)

    # Relationships
    jobs = relationship("ProcessingJob", back_populates="status_ref")

    # Audit fields inherited from Base


# Main Entity Tables
class AntibodySequence(Base):
    """Antibody sequence model."""

    __tablename__ = "antibody_sequences"

    # Primary key inherited from Base
    # id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())

    # Basic sequence information
    sequence = Column(Text, nullable=False, index=True)
    sequence_type = Column(String(50), nullable=False, default="AMINO_ACID")
    length = Column(Integer, nullable=False)

    # Metadata
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)

    # Validation and quality
    is_valid = Column(Boolean, nullable=False, default=True)
    validation_errors = Column(JSONB, nullable=True)

    # Relationships
    chains = relationship(
        "AntibodyChain",
        back_populates="sequence",
        cascade="all, delete-orphan",
    )
    features = relationship(
        "AntibodyFeature",
        back_populates="sequence",
        cascade="all, delete-orphan",
    )
    jobs = relationship("ProcessingJob", back_populates="sequence")

    # Audit fields inherited from Base
    # created_at, updated_at


class AntibodyChain(Base):
    """Antibody chain model."""

    __tablename__ = "antibody_chains"

    # Primary key inherited from Base

    # Foreign key to sequence
    sequence_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_sequences.id"), nullable=False
    )

    # Foreign keys to lookup tables
    chain_type_id = Column(
        UUID(as_uuid=True), ForeignKey("chain_types.id"), nullable=False
    )
    numbering_scheme_id = Column(
        UUID(as_uuid=True), ForeignKey("numbering_schemes.id"), nullable=False
    )

    # Chain information
    chain_identifier = Column(
        String(10), nullable=False
    )  # e.g., "H", "L", "A"
    sequence = Column(Text, nullable=False)
    length = Column(Integer, nullable=False)

    # Relationships
    sequence = relationship("AntibodySequence", back_populates="chains")
    chain_type_ref = relationship("ChainType", back_populates="chains")
    numbering_scheme_ref = relationship(
        "NumberingScheme", back_populates="chains"
    )
    domains = relationship(
        "AntibodyDomain", back_populates="chain", cascade="all, delete-orphan"
    )
    regions = relationship(
        "AntibodyRegion", back_populates="chain", cascade="all, delete-orphan"
    )
    features = relationship("AntibodyFeature", back_populates="chain")

    # Audit fields inherited from Base


class AntibodyDomain(Base):
    """Antibody domain model."""

    __tablename__ = "antibody_domains"

    # Primary key inherited from Base

    # Foreign key to chain
    chain_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_chains.id"), nullable=False
    )
    domain_type_id = Column(
        UUID(as_uuid=True), ForeignKey("domain_types.id"), nullable=False
    )

    # Domain information
    domain_name = Column(
        String(50), nullable=False
    )  # e.g., "VH", "CH1", "VL", "CL"
    sequence = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)

    # Confidence and quality
    confidence_score = Column(Float, nullable=True)
    quality_metrics = Column(JSONB, nullable=True)

    # Relationships
    chain = relationship("AntibodyChain", back_populates="domains")
    domain_type_ref = relationship("DomainType", back_populates="domains")
    regions = relationship(
        "AntibodyRegion", back_populates="domain", cascade="all, delete-orphan"
    )
    features = relationship("AntibodyFeature", back_populates="domain")

    # Audit fields inherited from Base


class AntibodyRegion(Base):
    """Antibody region model (FR1, CDR1, FR2, etc.)."""

    __tablename__ = "antibody_regions"

    # Primary key inherited from Base

    # Foreign keys
    chain_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_chains.id"), nullable=False
    )
    domain_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_domains.id"), nullable=True
    )
    region_type_id = Column(
        UUID(as_uuid=True), ForeignKey("region_types.id"), nullable=False
    )
    numbering_scheme_id = Column(
        UUID(as_uuid=True), ForeignKey("numbering_schemes.id"), nullable=False
    )

    # Region information
    sequence = Column(Text, nullable=False)
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)

    # Numbering information
    start_number = Column(Integer, nullable=True)
    end_number = Column(Integer, nullable=True)

    # Confidence and quality
    confidence_score = Column(Float, nullable=True)
    quality_metrics = Column(JSONB, nullable=True)

    # Relationships
    chain = relationship("AntibodyChain", back_populates="regions")
    domain = relationship("AntibodyDomain", back_populates="regions")
    region_type_ref = relationship("RegionType", back_populates="regions")
    numbering_scheme_ref = relationship(
        "NumberingScheme", back_populates="regions"
    )
    features = relationship("AntibodyFeature", back_populates="region")

    # Audit fields inherited from Base


class AntibodyFeature(Base):
    """Antibody feature model (mutations, post-translational modifications, etc.)."""

    __tablename__ = "antibody_features"

    # Primary key inherited from Base

    # Foreign keys
    sequence_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_sequences.id"), nullable=False
    )
    chain_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_chains.id"), nullable=True
    )
    domain_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_domains.id"), nullable=True
    )
    region_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_regions.id"), nullable=True
    )
    feature_type_id = Column(
        UUID(as_uuid=True), ForeignKey("feature_types.id"), nullable=False
    )

    # Feature information
    feature_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Position information
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)

    # Feature data
    feature_data = Column(JSONB, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Relationships
    sequence = relationship("AntibodySequence", back_populates="features")
    chain = relationship("AntibodyChain", back_populates="features")
    domain = relationship("AntibodyDomain", back_populates="features")
    region = relationship("AntibodyRegion", back_populates="features")
    feature_type_ref = relationship("FeatureType", back_populates="features")

    # Audit fields inherited from Base


class ProcessingJob(Base):
    """Processing job model for tracking annotation and analysis jobs."""

    __tablename__ = "processing_jobs"

    # Primary key inherited from Base

    # Foreign keys to lookup tables
    job_type_id = Column(
        UUID(as_uuid=True), ForeignKey("job_types.id"), nullable=False
    )
    status_id = Column(
        UUID(as_uuid=True), ForeignKey("job_statuses.id"), nullable=False
    )

    # Foreign key to sequence
    sequence_id = Column(
        UUID(as_uuid=True), ForeignKey("antibody_sequences.id"), nullable=True
    )

    # Input/Output
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)

    # Progress tracking
    progress = Column(Float, nullable=True, default=0.0)
    total_steps = Column(Integer, nullable=True)
    current_step = Column(Integer, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sequence = relationship("AntibodySequence", back_populates="jobs")
    job_type_ref = relationship("JobType", back_populates="jobs")
    status_ref = relationship("JobStatus", back_populates="jobs")

    # Audit fields inherited from Base
