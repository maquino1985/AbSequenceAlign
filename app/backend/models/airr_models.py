"""
Pydantic models for AIRR (Adaptive Immune Receptor Repertoire) format data.
These models represent the comprehensive data structure returned by IgBLAST
in AIRR format (outfmt 19) with advanced immunological annotations.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Locus(str, Enum):
    """Immunoglobulin/TCR locus"""

    IGH = "IGH"  # Immunoglobulin Heavy chain
    IGK = "IGK"  # Immunoglobulin Kappa light chain
    IGL = "IGL"  # Immunoglobulin Lambda light chain
    TRA = "TRA"  # T-cell Receptor Alpha chain
    TRB = "TRB"  # T-cell Receptor Beta chain
    TRG = "TRG"  # T-cell Receptor Gamma chain
    TRD = "TRD"  # T-cell Receptor Delta chain


class ProductivityStatus(str, Enum):
    """Sequence productivity status"""

    PRODUCTIVE = "T"  # In-frame, no stop codons
    UNPRODUCTIVE = "F"  # Out-of-frame or contains stop codons
    UNKNOWN = ""  # Cannot be determined


class FrameShiftStatus(str, Enum):
    """V gene frameshift status"""

    NO_FRAMESHIFT = "F"
    FRAMESHIFT = "T"
    UNKNOWN = ""


class AIRRAlignment(BaseModel):
    """AIRR alignment information for V, D, or J genes"""

    start: Optional[int] = Field(None, description="Alignment start position")
    end: Optional[int] = Field(None, description="Alignment end position")
    sequence_alignment: Optional[str] = Field(
        None, description="Aligned sequence"
    )
    sequence_alignment_aa: Optional[str] = Field(
        None, description="Aligned amino acid sequence"
    )
    germline_alignment: Optional[str] = Field(
        None, description="Aligned germline sequence"
    )
    germline_alignment_aa: Optional[str] = Field(
        None, description="Aligned germline amino acid sequence"
    )
    score: Optional[float] = Field(None, description="Alignment score")
    identity: Optional[float] = Field(
        None, description="Sequence identity percentage"
    )
    cigar: Optional[str] = Field(
        None, description="CIGAR string for alignment"
    )
    support: Optional[float] = Field(None, description="Support value")


class CDRRegion(BaseModel):
    """Complementarity Determining Region information"""

    sequence: Optional[str] = Field(
        None, description="CDR nucleotide sequence"
    )
    sequence_aa: Optional[str] = Field(
        None, description="CDR amino acid sequence"
    )
    start: Optional[int] = Field(None, description="CDR start position")
    end: Optional[int] = Field(None, description="CDR end position")


class FrameworkRegion(BaseModel):
    """Framework Region information"""

    sequence: Optional[str] = Field(
        None, description="FWR nucleotide sequence"
    )
    sequence_aa: Optional[str] = Field(
        None, description="FWR amino acid sequence"
    )
    start: Optional[int] = Field(None, description="FWR start position")
    end: Optional[int] = Field(None, description="FWR end position")


class JunctionRegion(BaseModel):
    """Junction/CDR3 region with detailed annotations"""

    junction: Optional[str] = Field(
        None, description="Full junction sequence (V-D-J)"
    )
    junction_aa: Optional[str] = Field(
        None, description="Junction amino acid sequence"
    )
    junction_length: Optional[int] = Field(
        None, description="Junction nucleotide length"
    )
    junction_aa_length: Optional[int] = Field(
        None, description="Junction amino acid length"
    )

    # CDR3 specific (subset of junction)
    cdr3: Optional[str] = Field(None, description="CDR3 nucleotide sequence")
    cdr3_aa: Optional[str] = Field(
        None, description="CDR3 amino acid sequence"
    )
    cdr3_start: Optional[int] = Field(None, description="CDR3 start position")
    cdr3_end: Optional[int] = Field(None, description="CDR3 end position")

    # N-regions (non-templated additions)
    np1: Optional[str] = Field(
        None, description="N1 region sequence (V-D junction)"
    )
    np1_length: Optional[int] = Field(None, description="N1 region length")
    np2: Optional[str] = Field(
        None, description="N2 region sequence (D-J junction)"
    )
    np2_length: Optional[int] = Field(None, description="N2 region length")


class SomaticMutationAnalysis(BaseModel):
    """Somatic hypermutation analysis"""

    v_mutations: Optional[int] = Field(
        None, description="Number of V gene mutations"
    )
    v_mutation_frequency: Optional[float] = Field(
        None, description="V gene mutation frequency"
    )
    silent_mutations: Optional[int] = Field(
        None, description="Number of silent mutations"
    )
    replacement_mutations: Optional[int] = Field(
        None, description="Number of replacement mutations"
    )
    replacement_to_silent_ratio: Optional[float] = Field(
        None, description="R/S ratio"
    )

    @field_validator("replacement_to_silent_ratio", mode="before")
    @classmethod
    def calculate_rs_ratio(cls, v, info):
        """Calculate R/S ratio if not provided"""
        if v is not None:
            return v
        silent = info.data.get("silent_mutations", 0)
        replacement = info.data.get("replacement_mutations", 0)
        if silent > 0:
            return replacement / silent
        return None


class AIRRRearrangement(BaseModel):
    """Complete AIRR rearrangement record with advanced annotations"""

    # Basic sequence information
    sequence_id: str = Field(..., description="Unique sequence identifier")
    sequence: str = Field(..., description="Full nucleotide sequence")
    sequence_aa: Optional[str] = Field(
        None, description="Translated amino acid sequence"
    )
    locus: Optional[Locus] = Field(
        None, description="Immunoglobulin/TCR locus"
    )

    # Productivity and quality annotations
    productive: Optional[ProductivityStatus] = Field(
        None, description="Productivity status"
    )
    stop_codon: Optional[bool] = Field(None, description="Contains stop codon")
    vj_in_frame: Optional[bool] = Field(
        None, description="V-J junction in frame"
    )
    v_frameshift: Optional[FrameShiftStatus] = Field(
        None, description="V gene frameshift status"
    )
    rev_comp: Optional[bool] = Field(
        None, description="Sequence is reverse complement"
    )
    complete_vdj: Optional[bool] = Field(
        None, description="Complete V(D)J rearrangement detected"
    )
    d_frame: Optional[int] = Field(None, description="D gene reading frame")

    # Gene assignments
    v_call: Optional[str] = Field(None, description="V gene assignment(s)")
    d_call: Optional[str] = Field(None, description="D gene assignment(s)")
    j_call: Optional[str] = Field(None, description="J gene assignment(s)")
    c_call: Optional[str] = Field(None, description="C gene assignment")

    # Sequence coordinates
    v_sequence_start: Optional[int] = Field(
        None, description="V gene start in sequence"
    )
    v_sequence_end: Optional[int] = Field(
        None, description="V gene end in sequence"
    )
    v_germline_start: Optional[int] = Field(
        None, description="V gene start in germline"
    )
    v_germline_end: Optional[int] = Field(
        None, description="V gene end in germline"
    )

    d_sequence_start: Optional[int] = Field(
        None, description="D gene start in sequence"
    )
    d_sequence_end: Optional[int] = Field(
        None, description="D gene end in sequence"
    )
    d_germline_start: Optional[int] = Field(
        None, description="D gene start in germline"
    )
    d_germline_end: Optional[int] = Field(
        None, description="D gene end in germline"
    )

    j_sequence_start: Optional[int] = Field(
        None, description="J gene start in sequence"
    )
    j_sequence_end: Optional[int] = Field(
        None, description="J gene end in sequence"
    )
    j_germline_start: Optional[int] = Field(
        None, description="J gene start in germline"
    )
    j_germline_end: Optional[int] = Field(
        None, description="J gene end in germline"
    )

    # Alignment details
    v_alignment: Optional[AIRRAlignment] = Field(
        None, description="V gene alignment details"
    )
    d_alignment: Optional[AIRRAlignment] = Field(
        None, description="D gene alignment details"
    )
    j_alignment: Optional[AIRRAlignment] = Field(
        None, description="J gene alignment details"
    )

    # Framework and CDR regions
    fwr1: Optional[FrameworkRegion] = Field(
        None, description="Framework region 1"
    )
    cdr1: Optional[CDRRegion] = Field(
        None, description="Complementarity determining region 1"
    )
    fwr2: Optional[FrameworkRegion] = Field(
        None, description="Framework region 2"
    )
    cdr2: Optional[CDRRegion] = Field(
        None, description="Complementarity determining region 2"
    )
    fwr3: Optional[FrameworkRegion] = Field(
        None, description="Framework region 3"
    )
    fwr4: Optional[FrameworkRegion] = Field(
        None, description="Framework region 4"
    )

    # Junction/CDR3 region
    junction_region: Optional[JunctionRegion] = Field(
        None, description="Junction/CDR3 region details"
    )

    # Advanced annotations
    somatic_mutations: Optional[SomaticMutationAnalysis] = Field(
        None, description="Somatic mutation analysis"
    )

    # Full sequence alignments
    sequence_alignment: Optional[str] = Field(
        None, description="Full sequence alignment"
    )
    germline_alignment: Optional[str] = Field(
        None, description="Full germline alignment"
    )
    sequence_alignment_aa: Optional[str] = Field(
        None, description="Full amino acid sequence alignment"
    )
    germline_alignment_aa: Optional[str] = Field(
        None, description="Full amino acid germline alignment"
    )

    @field_validator("productive", mode="before")
    @classmethod
    def parse_productive(cls, v):
        """Parse productivity status from various formats"""
        if v in ["T", "True", True, "productive"]:
            return ProductivityStatus.PRODUCTIVE
        elif v in ["F", "False", False, "unproductive"]:
            return ProductivityStatus.UNPRODUCTIVE
        return ProductivityStatus.UNKNOWN

    @field_validator("locus", mode="before")
    @classmethod
    def parse_locus(cls, v):
        """Parse locus from string"""
        if isinstance(v, str):
            v = v.upper()
            if v in ["IGH", "IGK", "IGL", "TRA", "TRB", "TRG", "TRD"]:
                return Locus(v)
        return v


class AIRRAnalysisResult(BaseModel):
    """Complete AIRR analysis result with multiple rearrangements"""

    rearrangements: List[AIRRRearrangement] = Field(
        ..., description="List of rearrangement records"
    )
    analysis_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis metadata"
    )

    # Summary statistics
    total_sequences: int = Field(
        ..., description="Total number of sequences analyzed"
    )
    productive_sequences: int = Field(
        0, description="Number of productive sequences"
    )
    unique_v_genes: List[str] = Field(
        default_factory=list, description="Unique V genes identified"
    )
    unique_j_genes: List[str] = Field(
        default_factory=list, description="Unique J genes identified"
    )
    unique_d_genes: List[str] = Field(
        default_factory=list, description="Unique D genes identified"
    )

    @field_validator("productive_sequences", mode="after")
    @classmethod
    def count_productive(cls, v, info):
        """Count productive sequences"""
        rearrangements = info.data.get("rearrangements", [])
        return sum(
            1
            for r in rearrangements
            if r.productive == ProductivityStatus.PRODUCTIVE
        )

    @field_validator("unique_v_genes", mode="after")
    @classmethod
    def extract_v_genes(cls, v, info):
        """Extract unique V genes"""
        rearrangements = info.data.get("rearrangements", [])
        v_genes = set()
        for r in rearrangements:
            if r.v_call:
                # Handle multiple assignments separated by commas
                genes = [g.strip() for g in r.v_call.split(",")]
                v_genes.update(genes)
        return sorted(list(v_genes))

    @field_validator("unique_j_genes", mode="after")
    @classmethod
    def extract_j_genes(cls, v, info):
        """Extract unique J genes"""
        rearrangements = info.data.get("rearrangements", [])
        j_genes = set()
        for r in rearrangements:
            if r.j_call:
                genes = [g.strip() for g in r.j_call.split(",")]
                j_genes.update(genes)
        return sorted(list(j_genes))

    @field_validator("unique_d_genes", mode="after")
    @classmethod
    def extract_d_genes(cls, v, info):
        """Extract unique D genes"""
        rearrangements = info.data.get("rearrangements", [])
        d_genes = set()
        for r in rearrangements:
            if r.d_call:
                genes = [g.strip() for g in r.d_call.split(",")]
                d_genes.update(genes)
        return sorted(list(d_genes))


class ClonalAnalysis(BaseModel):
    """Clonal analysis for repertoire-level insights"""

    clonotype_id: Optional[str] = Field(
        None, description="Clonotype identifier"
    )
    clone_size: Optional[int] = Field(
        None, description="Number of sequences in clone"
    )
    clone_frequency: Optional[float] = Field(
        None, description="Clone frequency in repertoire"
    )
    consensus_cdr3_aa: Optional[str] = Field(
        None, description="Consensus CDR3 amino acid sequence"
    )
    consensus_v_gene: Optional[str] = Field(
        None, description="Consensus V gene assignment"
    )
    consensus_j_gene: Optional[str] = Field(
        None, description="Consensus J gene assignment"
    )
    intraclonal_diversity: Optional[float] = Field(
        None, description="Diversity within clone"
    )


class RepertoireMetrics(BaseModel):
    """Repertoire-level diversity and usage metrics"""

    shannon_diversity: Optional[float] = Field(
        None, description="Shannon diversity index"
    )
    simpson_diversity: Optional[float] = Field(
        None, description="Simpson diversity index"
    )
    chao1_richness: Optional[float] = Field(
        None, description="Chao1 richness estimate"
    )

    # V gene usage
    v_gene_usage: Dict[str, float] = Field(
        default_factory=dict, description="V gene usage frequencies"
    )
    j_gene_usage: Dict[str, float] = Field(
        default_factory=dict, description="J gene usage frequencies"
    )
    d_gene_usage: Dict[str, float] = Field(
        default_factory=dict, description="D gene usage frequencies"
    )

    # CDR3 length distribution
    cdr3_length_distribution: Dict[int, int] = Field(
        default_factory=dict, description="CDR3 length distribution"
    )
    mean_cdr3_length: Optional[float] = Field(
        None, description="Mean CDR3 length"
    )
    median_cdr3_length: Optional[float] = Field(
        None, description="Median CDR3 length"
    )
