"""
SQLAlchemy models for the refactored biologic database schema.
This replaces the antibody-specific models with a more generic biologic structure.
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
class SequenceType(Base):
    """Sequence type lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "DNA", "RNA", "PROTEIN"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Deoxyribonucleic Acid", "Ribonucleic Acid", "Protein"
    description = Column(Text, nullable=True)

    # Relationships
    biologic_chains = relationship(
        "BiologicChain", back_populates="sequence_type_ref"
    )
    sequence_domains = relationship(
        "SequenceDomain", back_populates="sequence_type_ref"
    )

    # Audit fields inherited from Base


class ChainType(Base):
    """Chain type lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "HEAVY", "LIGHT", "SINGLE_CHAIN"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Heavy Chain", "Light Chain", "Single Chain"
    description = Column(Text, nullable=True)

    # Relationships
    biologic_chains = relationship(
        "BiologicChain", back_populates="chain_type_ref"
    )

    # Audit fields inherited from Base


class DomainType(Base):
    """Domain type lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "VARIABLE", "CONSTANT", "JOINING"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Variable Domain", "Constant Domain", "Joining Region"
    description = Column(Text, nullable=True)

    # Relationships
    sequence_domains = relationship(
        "SequenceDomain", back_populates="domain_type_ref"
    )

    # Audit fields inherited from Base


class NumberingScheme(Base):
    """Numbering scheme lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "IMGT", "KABAT", "CHOTHIA"
    name = Column(
        String(100), nullable=False
    )  # e.g., "IMGT Numbering", "Kabat Numbering", "Chothia Numbering"
    description = Column(Text, nullable=True)

    # Relationships
    biologic_chains = relationship(
        "BiologicChain", back_populates="numbering_scheme_ref"
    )
    sequence_regions = relationship(
        "SequenceRegion", back_populates="numbering_scheme_ref"
    )

    # Audit fields inherited from Base


class RegionType(Base):
    """Region type lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "FR1", "CDR1", "FR2", "CDR2", "FR3", "CDR3", "FR4"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Framework Region 1", "Complementarity-Determining Region 1"
    description = Column(Text, nullable=True)

    # Relationships
    sequence_regions = relationship(
        "SequenceRegion", back_populates="region_type_ref"
    )

    # Audit fields inherited from Base


class FeatureType(Base):
    """Feature type lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "GENE", "ALLELE", "ISOTYPE", "MUTATION", "POST_TRANSLATIONAL"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Gene", "Allele", "Isotype", "Mutation", "Post-Translational Modification"
    description = Column(Text, nullable=True)

    # Relationships
    domain_features = relationship(
        "DomainFeature", back_populates="feature_type_ref"
    )

    # Audit fields inherited from Base


class JobType(Base):
    """Job type lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "ANNOTATION", "ALIGNMENT", "ANALYSIS"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Sequence Annotation", "Sequence Alignment", "Sequence Analysis"
    description = Column(Text, nullable=True)

    # Relationships
    processing_jobs = relationship(
        "ProcessingJob", back_populates="job_type_ref"
    )

    # Audit fields inherited from Base


class JobStatus(Base):
    """Job status lookup table."""

    # Primary key inherited from Base
    code = Column(
        String(20), nullable=False, unique=True
    )  # e.g., "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"
    name = Column(
        String(100), nullable=False
    )  # e.g., "Pending", "Running", "Completed", "Failed", "Cancelled"
    description = Column(Text, nullable=True)

    # Relationships
    processing_jobs = relationship(
        "ProcessingJob", back_populates="status_ref"
    )

    # Audit fields inherited from Base


# Main Entity Tables
class Biologic(Base):
    """Biologic entity model - the main entity replacing antibody sequences."""

    # Primary key inherited from Base
    # id = Column(UUID(as_uuid=True), primary_key=True, default=UUIDv7())

    # Basic biologic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)

    # Validation and quality
    is_valid = Column(Boolean, nullable=False, default=True)
    validation_errors = Column(JSONB, nullable=True)

    # Relationships
    aliases = relationship(
        "BiologicAlias",
        back_populates="biologic",
        cascade="all, delete-orphan",
    )
    chains = relationship(
        "BiologicChain",
        back_populates="biologic",
        cascade="all, delete-orphan",
    )
    dna_sequences = relationship(
        "DNASequence",
        back_populates="biologic",
        cascade="all, delete-orphan",
    )
    rna_sequences = relationship(
        "RNASequence",
        back_populates="biologic",
        cascade="all, delete-orphan",
    )
    protein_sequences = relationship(
        "ProteinSequence",
        back_populates="biologic",
        cascade="all, delete-orphan",
    )
    processing_jobs = relationship("ProcessingJob", back_populates="biologic")

    # Audit fields inherited from Base
    # created_at, updated_at


class BiologicAlias(Base):
    """Biologic alias model for mapping multiple names to one biologic."""

    # Primary key inherited from Base

    # Foreign key to biologic
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=False
    )

    # Alias information
    alias = Column(String(255), nullable=False, index=True)
    alias_type = Column(
        String(50), nullable=True
    )  # e.g., "SYNONYM", "TRADE_NAME", "GENERIC_NAME"
    source = Column(String(255), nullable=True)

    # Relationships
    biologic = relationship("Biologic", back_populates="aliases")

    # Audit fields inherited from Base


class DNASequence(Base):
    """DNA sequence model."""

    # Primary key inherited from Base

    # Foreign key to biologic
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=False
    )

    # Sequence information
    sequence = Column(Text, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)

    # Validation and quality
    is_valid = Column(Boolean, nullable=False, default=True)

    # Relationships
    biologic = relationship("Biologic", back_populates="dna_sequences")

    # Audit fields inherited from Base


class RNASequence(Base):
    """RNA sequence model."""

    # Primary key inherited from Base

    # Foreign key to biologic
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=False
    )

    # Sequence information
    sequence = Column(Text, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)

    # Validation and quality
    is_valid = Column(Boolean, nullable=False, default=True)

    # Relationships
    biologic = relationship("Biologic", back_populates="rna_sequences")

    # Audit fields inherited from Base


class ProteinSequence(Base):
    """Protein sequence model."""

    # Primary key inherited from Base

    # Foreign key to biologic
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=False
    )

    # Sequence information
    sequence = Column(Text, nullable=False, index=True)
    length = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)

    # Validation and quality
    is_valid = Column(Boolean, nullable=False, default=True)

    # Relationships
    biologic = relationship("Biologic", back_populates="protein_sequences")

    # Audit fields inherited from Base


class BiologicChain(Base):
    """Biologic chain model - renamed from antibody chain."""

    # Primary key inherited from Base

    # Foreign key to biologic
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=False
    )

    # Foreign keys to lookup tables
    chain_type_id = Column(
        UUID(as_uuid=True), ForeignKey("chain_types.id"), nullable=False
    )
    numbering_scheme_id = Column(
        UUID(as_uuid=True), ForeignKey("numbering_schemes.id"), nullable=False
    )
    sequence_type_id = Column(
        UUID(as_uuid=True), ForeignKey("sequence_types.id"), nullable=False
    )

    # Chain information
    chain_identifier = Column(
        String(10), nullable=False
    )  # e.g., "H", "L", "A"
    sequence_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # References one of the sequence tables
    length = Column(Integer, nullable=False)

    # Relationships
    biologic = relationship("Biologic", back_populates="chains")
    chain_type_ref = relationship(
        "ChainType", back_populates="biologic_chains"
    )
    numbering_scheme_ref = relationship(
        "NumberingScheme", back_populates="biologic_chains"
    )
    sequence_type_ref = relationship(
        "SequenceType", back_populates="biologic_chains"
    )
    sequence_domains = relationship(
        "SequenceDomain", back_populates="chain", cascade="all, delete-orphan"
    )
    sequence_regions = relationship(
        "SequenceRegion", back_populates="chain", cascade="all, delete-orphan"
    )
    domain_features = relationship("DomainFeature", back_populates="chain")

    # Audit fields inherited from Base


class SequenceDomain(Base):
    """Sequence domain model - renamed from antibody domain."""

    # Primary key inherited from Base

    # Foreign key to chain
    chain_id = Column(
        UUID(as_uuid=True), ForeignKey("biologic_chains.id"), nullable=False
    )
    domain_type_id = Column(
        UUID(as_uuid=True), ForeignKey("domain_types.id"), nullable=False
    )
    sequence_type_id = Column(
        UUID(as_uuid=True), ForeignKey("sequence_types.id"), nullable=False
    )

    # Domain information
    domain_name = Column(
        String(50), nullable=False
    )  # e.g., "VH", "CH1", "VL", "CL"
    sequence_id = Column(
        UUID(as_uuid=True), nullable=True
    )  # References one of the sequence tables
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)

    # Confidence and quality
    confidence_score = Column(Float, nullable=True)
    quality_metrics = Column(JSONB, nullable=True)

    # Relationships
    chain = relationship("BiologicChain", back_populates="sequence_domains")
    domain_type_ref = relationship(
        "DomainType", back_populates="sequence_domains"
    )
    sequence_type_ref = relationship(
        "SequenceType", back_populates="sequence_domains"
    )
    sequence_regions = relationship(
        "SequenceRegion", back_populates="domain", cascade="all, delete-orphan"
    )
    domain_features = relationship("DomainFeature", back_populates="domain")

    # Audit fields inherited from Base


class SequenceRegion(Base):
    """Sequence region model - renamed from antibody region."""

    # Primary key inherited from Base

    # Foreign keys
    chain_id = Column(
        UUID(as_uuid=True), ForeignKey("biologic_chains.id"), nullable=False
    )
    domain_id = Column(
        UUID(as_uuid=True), ForeignKey("sequence_domains.id"), nullable=True
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
    chain = relationship("BiologicChain", back_populates="sequence_regions")
    domain = relationship("SequenceDomain", back_populates="sequence_regions")
    region_type_ref = relationship(
        "RegionType", back_populates="sequence_regions"
    )
    numbering_scheme_ref = relationship(
        "NumberingScheme", back_populates="sequence_regions"
    )
    domain_features = relationship("DomainFeature", back_populates="region")

    # Audit fields inherited from Base


class DomainFeature(Base):
    """Domain feature model - renamed from antibody feature."""

    # Primary key inherited from Base

    # Foreign keys
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=False
    )
    chain_id = Column(
        UUID(as_uuid=True), ForeignKey("biologic_chains.id"), nullable=True
    )
    domain_id = Column(
        UUID(as_uuid=True), ForeignKey("sequence_domains.id"), nullable=True
    )
    region_id = Column(
        UUID(as_uuid=True), ForeignKey("sequence_regions.id"), nullable=True
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
    biologic = relationship("Biologic", back_populates="domain_features")
    chain = relationship("BiologicChain", back_populates="domain_features")
    domain = relationship("SequenceDomain", back_populates="domain_features")
    region = relationship("SequenceRegion", back_populates="domain_features")
    feature_type_ref = relationship(
        "FeatureType", back_populates="domain_features"
    )

    # Audit fields inherited from Base


class ProcessingJob(Base):
    """Processing job model for tracking annotation and analysis jobs."""

    # Primary key inherited from Base

    # Foreign keys to lookup tables
    job_type_id = Column(
        UUID(as_uuid=True), ForeignKey("job_types.id"), nullable=False
    )
    status_id = Column(
        UUID(as_uuid=True), ForeignKey("job_statuses.id"), nullable=False
    )

    # Foreign key to biologic
    biologic_id = Column(
        UUID(as_uuid=True), ForeignKey("biologics.id"), nullable=True
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
    biologic = relationship("Biologic", back_populates="processing_jobs")
    job_type_ref = relationship("JobType", back_populates="processing_jobs")
    status_ref = relationship("JobStatus", back_populates="processing_jobs")

    # Audit fields inherited from Base
