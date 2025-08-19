"""
Database Discovery and Simplified IgBLAST API Endpoints

This module provides endpoints for discovering available databases
and executing IgBLAST with user-selected databases.
"""

import re
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query

from backend.core.exceptions import ExternalToolError
from backend.infrastructure.adapters.igblast_adapter_v3 import IgBlastAdapterV3
from backend.models.database_models import (
    DatabaseOption,
)
from backend.models.igblast_models import IgBlastRequest, IgBlastResponse

router = APIRouter(tags=["database"])


@router.get("/databases/igblast", response_model=Dict[str, Any])
async def get_igblast_databases():
    """Get available IgBLAST databases organized by organism and gene type."""
    try:
        adapter = IgBlastAdapterV3()
        databases = adapter.get_available_databases()

        # Convert to a more frontend-friendly format
        formatted_databases = {}
        for organism, gene_types in databases.items():
            formatted_databases[organism] = {}
            for gene_type, db_info in gene_types.items():
                formatted_databases[organism][gene_type] = DatabaseOption(
                    name=db_info["name"],
                    path=db_info["path"],
                    description=db_info["description"],
                    organism=organism,
                    gene_type=gene_type,
                )

        return {
            "success": True,
            "databases": formatted_databases,
            "organisms": list(databases.keys()),
            "gene_types": ["V", "D", "J", "C"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get databases: {str(e)}"
        )


@router.get("/databases/blast", response_model=Dict[str, Any])
async def get_blast_databases():
    """Get available BLAST databases."""
    try:
        adapter = IgBlastAdapterV3()
        databases = adapter.get_blast_databases()

        return {"success": True, "databases": databases}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get BLAST databases: {str(e)}"
        )


@router.post("/igblast/execute", response_model=IgBlastResponse)
async def execute_igblast(request: IgBlastRequest):
    """Execute IgBLAST with user-selected databases."""
    try:
        adapter = IgBlastAdapterV3()

        # Validate and clean sequence
        sequence = re.sub(r"[\s\n\r]", "", request.query_sequence).upper()
        if not sequence:
            raise HTTPException(
                status_code=400, detail="Query sequence cannot be empty"
            )

        # Execute IgBLAST
        result = adapter.execute(
            query_sequence=sequence,
            v_db=request.v_db,
            d_db=request.d_db,
            j_db=request.j_db,
            c_db=request.c_db,
            blast_type=request.blast_type,
            use_airr_format=request.use_airr_format,
        )

        return IgBlastResponse(
            success=True,
            result=result,
            databases_used=result.get("databases_used", {}),
            total_hits=result.get("total_hits", 0),
        )

    except ExternalToolError as e:
        raise HTTPException(
            status_code=500, detail=f"IgBLAST execution failed: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}"
        )


@router.get("/databases/validate")
async def validate_database_path(
    db_path: str = Query(..., description="Database path to validate")
):
    """Validate if a database path exists and is accessible."""
    try:
        adapter = IgBlastAdapterV3()
        is_valid = adapter._validate_database_path(db_path)

        return {"success": True, "is_valid": is_valid, "db_path": db_path}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Validation failed: {str(e)}"
        )


@router.get("/databases/suggestions")
async def get_database_suggestions(
    organism: str = Query(..., description="Organism (human, mouse, rhesus)"),
    gene_type: str = Query(..., description="Gene type (V, D, J, C)"),
):
    """Get database suggestions for a specific organism and gene type."""
    try:
        adapter = IgBlastAdapterV3()
        databases = adapter.get_available_databases()

        if organism not in databases:
            raise HTTPException(
                status_code=404, detail=f"Organism '{organism}' not found"
            )

        if gene_type not in databases[organism]:
            raise HTTPException(
                status_code=404,
                detail=f"Gene type '{gene_type}' not found for organism '{organism}'",
            )

        db_info = databases[organism][gene_type]

        return {
            "success": True,
            "suggestion": DatabaseOption(
                name=db_info["name"],
                path=db_info["path"],
                description=db_info["description"],
                organism=organism,
                gene_type=gene_type,
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get suggestions: {str(e)}"
        )
