"""
IgBLAST-related Pydantic models for API v2.
"""

from typing import Optional

from pydantic import BaseModel, Field


class IgBlastRequest(BaseModel):
    """IgBLAST execution request model."""

    query_sequence: str = Field(..., description="Query sequence to analyze")
    v_db: str = Field(..., description="V gene database path")
    d_db: Optional[str] = Field(
        None, description="D gene database path (optional)"
    )
    j_db: Optional[str] = Field(
        None, description="J gene database path (optional)"
    )
    c_db: Optional[str] = Field(
        None, description="C gene database path (optional)"
    )
    blast_type: str = Field(
        "igblastn", description="BLAST type (igblastn or igblastp)"
    )
    use_airr_format: bool = Field(False, description="Use AIRR format output")


class FrameworkCDRRegion(BaseModel):
    """Framework or CDR region information."""

    start: Optional[int] = Field(
        None, description="Start position in sequence"
    )
    end: Optional[int] = Field(None, description="End position in sequence")
    length: Optional[int] = Field(None, description="Region length")
    matches: Optional[int] = Field(
        None, description="Number of matching residues"
    )
    mismatches: Optional[int] = Field(
        None, description="Number of mismatched residues"
    )
    gaps: Optional[int] = Field(None, description="Number of gaps")
    percent_identity: Optional[float] = Field(
        None, description="Percent identity for this region"
    )


class IgBlastAnalysisSummary(BaseModel):
    """Summary of IgBLAST analysis including framework and CDR regions."""

    # Gene assignments
    v_gene: Optional[str] = Field(None, description="V gene assignment")
    d_gene: Optional[str] = Field(None, description="D gene assignment")
    j_gene: Optional[str] = Field(None, description="J gene assignment")
    c_gene: Optional[str] = Field(None, description="C gene assignment")

    # Chain and productivity information
    chain_type: Optional[str] = Field(
        None, description="Chain type (heavy/light)"
    )
    productive: Optional[str] = Field(None, description="Productivity status")
    stop_codon: Optional[str] = Field(
        None, description="Stop codon information"
    )
    v_j_frame: Optional[str] = Field(None, description="V-J frame information")
    strand: Optional[str] = Field(None, description="Strand orientation")

    # CDR3 information
    cdr3_sequence: Optional[str] = Field(
        None, description="CDR3 nucleotide sequence"
    )
    cdr3_aa: Optional[str] = Field(
        None, description="CDR3 amino acid sequence"
    )
    cdr3_start: Optional[int] = Field(None, description="CDR3 start position")
    cdr3_end: Optional[int] = Field(None, description="CDR3 end position")

    # Framework and CDR regions (for protein IgBLAST)
    fr1_start: Optional[int] = Field(
        None, description="Framework 1 start position"
    )
    fr1_end: Optional[int] = Field(
        None, description="Framework 1 end position"
    )
    fr1_length: Optional[int] = Field(None, description="Framework 1 length")
    fr1_matches: Optional[int] = Field(None, description="Framework 1 matches")
    fr1_mismatches: Optional[int] = Field(
        None, description="Framework 1 mismatches"
    )
    fr1_gaps: Optional[int] = Field(None, description="Framework 1 gaps")
    fr1_percent_identity: Optional[float] = Field(
        None, description="Framework 1 percent identity"
    )

    cdr1_start: Optional[int] = Field(None, description="CDR1 start position")
    cdr1_end: Optional[int] = Field(None, description="CDR1 end position")
    cdr1_length: Optional[int] = Field(None, description="CDR1 length")
    cdr1_matches: Optional[int] = Field(None, description="CDR1 matches")
    cdr1_mismatches: Optional[int] = Field(None, description="CDR1 mismatches")
    cdr1_gaps: Optional[int] = Field(None, description="CDR1 gaps")
    cdr1_percent_identity: Optional[float] = Field(
        None, description="CDR1 percent identity"
    )

    fr2_start: Optional[int] = Field(
        None, description="Framework 2 start position"
    )
    fr2_end: Optional[int] = Field(
        None, description="Framework 2 end position"
    )
    fr2_length: Optional[int] = Field(None, description="Framework 2 length")
    fr2_matches: Optional[int] = Field(None, description="Framework 2 matches")
    fr2_mismatches: Optional[int] = Field(
        None, description="Framework 2 mismatches"
    )
    fr2_gaps: Optional[int] = Field(None, description="Framework 2 gaps")
    fr2_percent_identity: Optional[float] = Field(
        None, description="Framework 2 percent identity"
    )

    cdr2_start: Optional[int] = Field(None, description="CDR2 start position")
    cdr2_end: Optional[int] = Field(None, description="CDR2 end position")
    cdr2_length: Optional[int] = Field(None, description="CDR2 length")
    cdr2_matches: Optional[int] = Field(None, description="CDR2 matches")
    cdr2_mismatches: Optional[int] = Field(None, description="CDR2 mismatches")
    cdr2_gaps: Optional[int] = Field(None, description="CDR2 gaps")
    cdr2_percent_identity: Optional[float] = Field(
        None, description="CDR2 percent identity"
    )

    fr3_start: Optional[int] = Field(
        None, description="Framework 3 start position"
    )
    fr3_end: Optional[int] = Field(
        None, description="Framework 3 end position"
    )
    fr3_length: Optional[int] = Field(None, description="Framework 3 length")
    fr3_matches: Optional[int] = Field(None, description="Framework 3 matches")
    fr3_mismatches: Optional[int] = Field(
        None, description="Framework 3 mismatches"
    )
    fr3_gaps: Optional[int] = Field(None, description="Framework 3 gaps")
    fr3_percent_identity: Optional[float] = Field(
        None, description="Framework 3 percent identity"
    )


class IgBlastResponse(BaseModel):
    """IgBLAST execution response model."""

    success: bool = Field(
        ..., description="Whether the execution was successful"
    )
    result: dict = Field(..., description="IgBLAST analysis results")
    databases_used: dict = Field(
        ..., description="Databases used in the analysis"
    )
    total_hits: int = Field(..., description="Total number of hits found")
