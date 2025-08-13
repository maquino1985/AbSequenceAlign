"""
Pydantic models for Biologic entities.

IMPORTANT: These models must be kept in sync with ORM models in:
- backend.database.models.biologic.Biologic
- backend.database.models.biologic.BiologicAlias
- backend.database.models.biologic.Chain
- backend.database.models.biologic.Sequence
- backend.database.models.biologic.ChainSequence
- backend.database.models.biologic.SequenceDomain
- backend.database.models.biologic.DomainFeature

When updating ORM models, update these Pydantic models accordingly.
Use the model validation tests in tests/test_model_compatibility.py to catch mismatches.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class BiologicResponse(BaseModel):
    """Response model for Biologic entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match Biologic ORM model)
    id: UUID
    name: str
    description: Optional[str] = None
    organism: Optional[str] = None
    biologic_type: str = "antibody"
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class BiologicCreate(BaseModel):
    """Request model for creating Biologic entity"""

    name: str = Field(..., description="Primary name for the biologic")
    description: Optional[str] = Field(
        None, description="Description of the biologic"
    )
    organism: Optional[str] = Field(None, description="Source organism")
    biologic_type: str = Field(
        "antibody", description="Type of biologic (antibody, enzyme, etc.)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class BiologicUpdate(BaseModel):
    """Request model for updating Biologic entity"""

    name: Optional[str] = None
    description: Optional[str] = None
    organism: Optional[str] = None
    biologic_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BiologicAliasResponse(BaseModel):
    """Response model for BiologicAlias entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match BiologicAlias ORM model)
    id: UUID
    biologic_id: UUID
    alias: str
    alias_type: str
    is_primary: bool
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class BiologicAliasCreate(BaseModel):
    """Request model for creating BiologicAlias entity"""

    alias: str = Field(..., description="Alias name")
    alias_type: str = Field(
        ...,
        description="Type of alias (common_name, scientific_name, trade_name, etc.)",
    )
    is_primary: bool = Field(
        False, description="Whether this is the primary alias"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChainResponse(BaseModel):
    """Response model for Chain entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match Chain ORM model)
    id: UUID
    biologic_id: UUID
    name: str
    chain_type: str
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ChainCreate(BaseModel):
    """Request model for creating Chain entity"""

    name: str = Field(..., description="Name of the chain")
    chain_type: str = Field(
        ..., description="Type of chain (HEAVY, LIGHT, SINGLE_CHAIN, etc.)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SequenceResponse(BaseModel):
    """Response model for Sequence entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match Sequence ORM model)
    id: UUID
    sequence_type: str  # PROTEIN, DNA, RNA
    sequence_data: str
    length: int
    description: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SequenceCreate(BaseModel):
    """Request model for creating Sequence entity"""

    sequence_type: str = Field(
        ..., description="Type of sequence (PROTEIN, DNA, RNA)"
    )
    sequence_data: str = Field(..., description="The actual sequence data")
    description: Optional[str] = Field(
        None, description="Description of the sequence"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChainSequenceResponse(BaseModel):
    """Response model for ChainSequence entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match ChainSequence ORM model)
    id: UUID
    chain_id: UUID
    sequence_id: UUID
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ChainSequenceCreate(BaseModel):
    """Request model for creating ChainSequence entity"""

    sequence_id: UUID = Field(..., description="ID of the sequence")
    start_position: Optional[int] = Field(
        None, description="Start position in the sequence"
    )
    end_position: Optional[int] = Field(
        None, description="End position in the sequence"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SequenceDomainResponse(BaseModel):
    """Response model for SequenceDomain entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match SequenceDomain ORM model)
    id: UUID
    chain_sequence_id: UUID
    domain_type: str
    start_position: int
    end_position: int
    species: Optional[str] = None
    germline: Optional[str] = None
    confidence_score: Optional[int] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SequenceDomainCreate(BaseModel):
    """Request model for creating SequenceDomain entity"""

    domain_type: str = Field(
        ..., description="Type of domain (VARIABLE, CONSTANT, LINKER, etc.)"
    )
    start_position: int = Field(
        ..., description="Start position in the sequence"
    )
    end_position: int = Field(..., description="End position in the sequence")
    species: Optional[str] = Field(
        None,
        description="Species the domain was annotated against (e.g., human, mouse, rat)",
    )
    germline: Optional[str] = Field(
        None,
        description="Best matching germline gene (e.g., IGHV1-2*02, IGHG1*01)",
    )
    confidence_score: Optional[int] = Field(
        None, ge=0, le=100, description="Confidence score (0-100)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DomainFeatureResponse(BaseModel):
    """Response model for DomainFeature entity"""

    model_config = ConfigDict(from_attributes=True)

    # Core fields (must match DomainFeature ORM model)
    id: UUID
    sequence_domain_id: UUID
    feature_type: str
    name: str
    value: str
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    confidence_score: Optional[int] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class DomainFeatureCreate(BaseModel):
    """Request model for creating DomainFeature entity"""

    feature_type: str = Field(
        ..., description="Type of feature (CDR, FR, MUTATION, etc.)"
    )
    name: str = Field(..., description="Name of the feature")
    value: str = Field(..., description="Value of the feature")
    start_position: Optional[int] = Field(
        None, description="Start position in the domain"
    )
    end_position: Optional[int] = Field(
        None, description="End position in the domain"
    )
    confidence_score: Optional[int] = Field(
        None, ge=0, le=100, description="Confidence score (0-100)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Update forward references
BiologicResponse.model_rebuild()
ChainResponse.model_rebuild()
ChainSequenceResponse.model_rebuild()
SequenceDomainResponse.model_rebuild()
