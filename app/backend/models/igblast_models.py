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
