from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
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

    # Common chain patterns
    heavy_chain: Optional[str] = Field(None, description="Heavy chain sequence")
    light_chain: Optional[str] = Field(None, description="Light chain sequence")
    scfv: Optional[str] = Field(None, description="Single-chain Fv sequence")

    # Variable chain patterns (e.g., heavy_chain_1, heavy_chain_2, etc.)
    heavy_chain_1: Optional[str] = Field(None, description="First heavy chain sequence")
    heavy_chain_2: Optional[str] = Field(
        None, description="Second heavy chain sequence"
    )
    heavy_chain_3: Optional[str] = Field(None, description="Third heavy chain sequence")
    heavy_chain_4: Optional[str] = Field(
        None, description="Fourth heavy chain sequence"
    )

    light_chain_1: Optional[str] = Field(None, description="First light chain sequence")
    light_chain_2: Optional[str] = Field(
        None, description="Second light chain sequence"
    )
    light_chain_3: Optional[str] = Field(None, description="Third light chain sequence")
    light_chain_4: Optional[str] = Field(
        None, description="Fourth light chain sequence"
    )

    # Additional custom chains
    custom_chains: Optional[Dict[str, str]] = Field(
        None, description="Additional custom chain sequences with arbitrary labels"
    )

    @field_validator(
        "heavy_chain",
        "light_chain",
        "scfv",
        "heavy_chain_1",
        "heavy_chain_2",
        "heavy_chain_3",
        "heavy_chain_4",
        "light_chain_1",
        "light_chain_2",
        "light_chain_3",
        "light_chain_4",
        mode="before",
    )
    @classmethod
    def validate_chain_sequences(cls, v, info):
        """Validate that chain sequences are valid amino acid sequences"""
        if v is not None:
            # Basic validation - check for valid amino acids
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            invalid_chars = set(v.upper()) - valid_aa
            if invalid_chars:
                raise ValueError(
                    f"Invalid amino acids in {info.field_name}: {invalid_chars}"
                )

            # Check minimum length
            if len(v) < 15:
                raise ValueError(
                    f"{info.field_name} sequence too short ({len(v)} AA). Minimum 15 AA required."
                )

        return v

    def get_all_chains(self) -> Dict[str, str]:
        """Get all chain sequences as a dictionary.
        Do not split scFv; keep it as a single chain so domain offsets remain relative to the original sequence.
        """
        chains = {}

        # Add standard chains if present (including scfv as-is)
        for field_name, value in self.model_dump().items():
            if field_name not in ["name", "custom_chains"] and value is not None:
                chains[field_name] = value

        # Add custom chains if present
        if self.custom_chains:
            chains.update(self.custom_chains)

        return chains


class UploadRequest(BaseModel):
    """Request model for sequence upload"""

    sequences: List[str] = Field(
        ..., description="List of protein sequences in FASTA format"
    )
    chain_type: Optional[ChainType] = Field(None, description="Expected chain type")
    species: Optional[str] = Field(None, description="Species (e.g., human, mouse)")


class AlignmentRequest(BaseModel):
    """Request model for sequence alignment"""

    dataset_id: str = Field(..., description="Dataset ID from upload")
    method: AlignmentMethod = Field(..., description="Alignment method to use")
    numbering_scheme: NumberingScheme = Field(
        default=NumberingScheme.IMGT, description="Numbering scheme"
    )
    gap_open: float = Field(default=-10.0, description="Gap opening penalty")
    gap_extend: float = Field(default=-0.5, description="Gap extension penalty")
    matrix: str = Field(default="BLOSUM62", description="Substitution matrix")


class AnnotationRequest(BaseModel):
    """Request model for sequence annotation"""

    sequences: List[SequenceInput] = Field(
        ..., description="List of sequences with names and variable chain data"
    )
    numbering_scheme: NumberingScheme = Field(
        default=NumberingScheme.IMGT, description="Numbering scheme"
    )
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


class MSASequence(BaseModel):
    """Individual sequence in MSA with annotations"""

    name: str = Field(..., description="Sequence name/identifier")
    original_sequence: str = Field(..., description="Original unaligned sequence")
    aligned_sequence: str = Field(..., description="Aligned sequence with gaps")
    start_position: int = Field(..., description="Start position in alignment")
    end_position: int = Field(..., description="End position in alignment")
    gaps: List[int] = Field(default_factory=list, description="Positions with gaps")
    annotations: Optional[List[Dict[str, Any]]] = Field(
        None, description="Region annotations"
    )


class MSAResult(BaseModel):
    """Result of multiple sequence alignment"""

    msa_id: str = Field(..., description="Unique MSA identifier")
    sequences: List[MSASequence] = Field(..., description="Aligned sequences")
    alignment_matrix: List[List[str]] = Field(
        ..., description="2D array of aligned sequences"
    )
    consensus: str = Field(..., description="Consensus sequence")
    alignment_method: AlignmentMethod = Field(
        ..., description="Method used for alignment"
    )
    created_at: str = Field(..., description="Creation timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class MSAAnnotationResult(BaseModel):
    """Result of MSA annotation"""

    msa_id: str = Field(..., description="MSA identifier")
    annotated_sequences: List[MSASequence] = Field(
        ..., description="Sequences with annotations"
    )
    numbering_scheme: NumberingScheme = Field(..., description="Numbering scheme used")
    region_mappings: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Region mappings across sequences"
    )


class MSACreationRequest(BaseModel):
    """Request model for MSA creation"""

    sequences: List[SequenceInput] = Field(..., description="Sequences to align")
    alignment_method: AlignmentMethod = Field(
        default=AlignmentMethod.MUSCLE, description="Alignment method"
    )
    numbering_scheme: NumberingScheme = Field(
        default=NumberingScheme.IMGT, description="Numbering scheme for annotation"
    )


class MSAAnnotationRequest(BaseModel):
    """Request model for MSA annotation"""

    msa_id: str = Field(..., description="MSA identifier")
    numbering_scheme: NumberingScheme = Field(
        default=NumberingScheme.IMGT, description="Numbering scheme"
    )


class MSAJobStatus(BaseModel):
    """Status of MSA job"""

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(
        ..., description="Job status: pending, running, completed, failed"
    )
    progress: float = Field(default=0.0, description="Progress percentage")
    message: str = Field(..., description="Status message")
    result: Optional[Dict[str, Any]] = Field(
        None, description="Job result when completed"
    )
    created_at: str = Field(..., description="Job creation timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")


class APIResponse(BaseModel):
    """Standard API response wrapper"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
