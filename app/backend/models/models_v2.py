from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from enum import Enum


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

