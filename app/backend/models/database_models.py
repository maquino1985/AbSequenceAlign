"""
Database-related Pydantic models for API v2.
"""

from typing import Optional
from pydantic import BaseModel, Field


class DatabaseOption(BaseModel):
    """Database option model for frontend selection."""

    name: str = Field(..., description="Human-readable database name")
    path: str = Field(..., description="Database file path")
    description: str = Field(..., description="Database description")
    organism: str = Field(..., description="Organism (human, mouse, rhesus)")
    gene_type: str = Field(..., description="Gene type (V, D, J, C)")


class DatabaseSelection(BaseModel):
    """Database selection model for IgBLAST execution."""

    v_db: str = Field(..., description="V gene database path (required)")
    d_db: Optional[str] = Field(
        None, description="D gene database path (optional)"
    )
    j_db: Optional[str] = Field(
        None, description="J gene database path (optional)"
    )
    c_db: Optional[str] = Field(
        None, description="C gene database path (optional)"
    )


class DatabaseValidationRequest(BaseModel):
    """Database validation request model."""

    db_path: str = Field(..., description="Database path to validate")


class DatabaseSuggestionRequest(BaseModel):
    """Database suggestion request model."""

    organism: str = Field(..., description="Organism (human, mouse, rhesus)")
    gene_type: str = Field(..., description="Gene type (V, D, J, C)")
