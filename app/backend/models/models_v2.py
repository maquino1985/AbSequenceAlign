from enum import Enum
from typing import List, Optional, Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class DomainType(str, Enum):
    VARIABLE = "V"
    CONSTANT = "C"
    LINKER = "LINKER"


class RegionFeature(BaseModel):
    kind: str = Field(..., description="Type of feature, e.g., 'sequence'")
    value: Any = Field(..., description="Feature value")


class Region(BaseModel):
    name: str
    start: int
    stop: int
    features: List[RegionFeature] = Field(default_factory=list)


class Domain(BaseModel):
    domain_type: DomainType = Field(default=DomainType.VARIABLE)
    start: Optional[int] = None
    stop: Optional[int] = None
    sequence: Optional[str] = None
    regions: List[Region] = Field(default_factory=list)
    isotype: Optional[str] = None
    species: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Chain(BaseModel):
    name: str
    sequence: str
    domains: List[Domain] = Field(default_factory=list)


class Sequence(BaseModel):
    name: str
    original_sequence: str
    chains: List[Chain] = Field(default_factory=list)


class AnnotationResult(BaseModel):
    sequences: List[Sequence]
    numbering_scheme: str
    total_sequences: int
    chain_types: Dict[str, int] = Field(default_factory=dict)
    isotypes: Dict[str, int] = Field(default_factory=dict)
    species: Dict[str, int] = Field(default_factory=dict)


# New models that match the ORM structure
class LookupTableBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: Optional[str] = None


class ChainType(LookupTableBase):
    pass


class DomainTypeLookup(LookupTableBase):
    pass


class NumberingSchemeLookup(LookupTableBase):
    pass


class RegionTypeLookup(LookupTableBase):
    pass


class FeatureTypeLookup(LookupTableBase):
    pass


class AntibodyFeature(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    feature_name: str
    description: Optional[str] = None
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    feature_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    feature_type: FeatureTypeLookup


class AntibodyRegion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sequence: str
    start_position: int
    end_position: int
    length: int
    start_number: Optional[int] = None
    end_number: Optional[int] = None
    confidence_score: Optional[float] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    region_type: RegionTypeLookup
    numbering_scheme: NumberingSchemeLookup
    features: List[AntibodyFeature] = Field(default_factory=list)


class AntibodyDomain(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    domain_name: str
    sequence: str
    start_position: int
    end_position: int
    length: int
    confidence_score: Optional[float] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    domain_type: DomainTypeLookup
    regions: List[AntibodyRegion] = Field(default_factory=list)
    features: List[AntibodyFeature] = Field(default_factory=list)


class AntibodyChain(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chain_identifier: str
    sequence: str
    length: int
    chain_type: ChainType
    numbering_scheme: NumberingSchemeLookup
    domains: List[AntibodyDomain] = Field(default_factory=list)
    regions: List[AntibodyRegion] = Field(default_factory=list)
    features: List[AntibodyFeature] = Field(default_factory=list)


class AntibodySequence(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sequence: str
    sequence_type: str = "AMINO_ACID"
    length: int
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    is_valid: bool = True
    validation_errors: Optional[Dict[str, Any]] = None
    chains: List[AntibodyChain] = Field(default_factory=list)
    features: List[AntibodyFeature] = Field(default_factory=list)


class AnnotationResultV2(BaseModel):
    sequences: List[AntibodySequence]
    numbering_scheme: str
    total_sequences: int
    chain_types: Dict[str, int] = Field(default_factory=dict)
    isotypes: Dict[str, int] = Field(default_factory=dict)
    species: Dict[str, int] = Field(default_factory=dict)
