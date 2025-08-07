from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class NumberingScheme(str, Enum):
    """Antibody numbering schemes supported by ANARCI"""
    IMGT = "imgt"
    KABAT = "kabat"
    CHOTHIA = "chothia"
    MARTIN = "martin"
    AHO = "aho"
    CGG = "cgg"


class AlignmentMethod(str, Enum):
    """Available alignment methods"""
    PAIRWISE_GLOBAL = "pairwise_global"
    PAIRWISE_LOCAL = "pairwise_local"
    MUSCLE = "muscle"
    MAFFT = "mafft"
    CLUSTALO = "clustalo"
    CUSTOM_ANTIBODY = "custom_antibody"


class ChainType(str, Enum):
    """Antibody chain types"""
    HEAVY = "H"
    LIGHT = "L"
    KAPPA = "K"
    LAMBDA = "L"
    BETA = "B"
    GAMMA = "G"
    DELTA = "D"
    EPSILON = "E"
    ZETA = "Z"
    ALPHA = "A"
    THETA = "T"
    IOTA = "I"


class SequenceInput(BaseModel):
    """Individual sequence input with name and variable chain data"""
    name: str = Field(..., description="Name/identifier for the sequence")
    # Allow any additional fields as chain labels with sequence values
    class Config:
        extra = "allow"  # Allow additional fields beyond 'name'


class UploadRequest(BaseModel):
    """Request model for sequence upload"""
    sequences: List[str] = Field(..., description="List of protein sequences in FASTA format")
    chain_type: Optional[ChainType] = Field(None, description="Expected chain type")
    species: Optional[str] = Field(None, description="Species (e.g., human, mouse)")


class AlignmentRequest(BaseModel):
    """Request model for sequence alignment"""
    dataset_id: str = Field(..., description="Dataset ID from upload")
    method: AlignmentMethod = Field(..., description="Alignment method to use")
    numbering_scheme: NumberingScheme = Field(default=NumberingScheme.IMGT, description="Numbering scheme")
    gap_open: float = Field(default=-10.0, description="Gap opening penalty")
    gap_extend: float = Field(default=-0.5, description="Gap extension penalty")
    matrix: str = Field(default="BLOSUM62", description="Substitution matrix")


class AnnotationRequest(BaseModel):
    """Request model for sequence annotation"""
    sequences: List[SequenceInput] = Field(..., description="List of sequences with names and variable chain data")
    numbering_scheme: NumberingScheme = Field(default=NumberingScheme.IMGT, description="Numbering scheme")
    chain_type: Optional[ChainType] = Field(None, description="Expected chain type")


class SequenceInfo(BaseModel):
    """Information about a single sequence"""
    sequence: str
    name: Optional[str] = None
    chain_type: Optional[str] = None
    isotype: Optional[str] = None
    species: Optional[str] = None
    germline: Optional[str] = None
    regions: Optional[Dict[str, Any]] = None


class AnnotationResult(BaseModel):
    """Result of sequence annotation"""
    sequences: List[SequenceInfo]
    numbering_scheme: NumberingScheme
    total_sequences: int
    chain_types: Dict[str, int]
    isotypes: Dict[str, int]
    species: Dict[str, int]


class AlignmentResult(BaseModel):
    """Result of sequence alignment"""
    dataset_id: str
    method: AlignmentMethod
    alignment: str  # FASTA format
    statistics: Dict[str, Any]
    numbering_scheme: NumberingScheme


class DatasetInfo(BaseModel):
    """Information about a dataset"""
    dataset_id: str
    sequence_count: int
    created_at: str
    status: str  # "uploaded", "annotated", "aligned", "error"


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
