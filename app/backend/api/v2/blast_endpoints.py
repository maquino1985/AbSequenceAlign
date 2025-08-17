"""
BLAST API endpoints for sequence similarity search.
Provides endpoints for BLAST and IgBLAST operations.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from ...services import BlastService, IgBlastService
from ...logger import logger

router = APIRouter()


class BlastSearchRequest(BaseModel):
    """Request model for BLAST search"""

    query_sequence: str
    databases: List[str]
    blast_type: str = "blastp"
    evalue: float = 1e-10
    max_target_seqs: int = 10
    organism: Optional[str] = None  # For IgBLAST


class BlastSearchResponse(BaseModel):
    """Response model for BLAST search"""

    success: bool
    message: str
    data: Dict[str, Any]


class CustomDatabaseRequest(BaseModel):
    """Request model for creating custom database"""

    sequences: List[Dict[str, str]]  # List of {name, sequence} dicts
    database_name: str
    database_type: str = "protein"


@router.get("/health")
async def blast_health_check():
    """Health check for BLAST endpoints"""
    return {"status": "healthy", "service": "blast"}


@router.get("/databases")
async def get_available_databases():
    """Get list of available BLAST databases"""
    try:
        blast_service = BlastService()
        databases = blast_service.get_available_databases()

        return BlastSearchResponse(
            success=True,
            message="Available databases retrieved successfully",
            data={"databases": databases},
        )
    except Exception as e:
        logger.error(f"Failed to get databases: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get databases: {e}"
        )


@router.post("/search/public", response_model=BlastSearchResponse)
async def search_public_databases(request: BlastSearchRequest):
    """Search sequences against public databases"""
    try:
        blast_service = BlastService()

        results = blast_service.search_public_databases(
            query_sequence=request.query_sequence,
            databases=request.databases,
            blast_type=request.blast_type,
            evalue=request.evalue,
            max_target_seqs=request.max_target_seqs,
        )

        return BlastSearchResponse(
            success=True,
            message=f"BLAST search completed successfully",
            data={"results": results},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"BLAST search failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"BLAST search failed: {e}"
        )


@router.post("/search/internal", response_model=BlastSearchResponse)
async def search_internal_database(request: BlastSearchRequest):
    """Search sequences against internal database"""
    try:
        blast_service = BlastService()

        results = blast_service.search_internal_database(
            query_sequence=request.query_sequence,
            blast_type=request.blast_type,
            evalue=request.evalue,
            max_target_seqs=request.max_target_seqs,
        )

        return BlastSearchResponse(
            success=True,
            message=f"Internal BLAST search completed successfully",
            data={"results": results},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal BLAST search failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal BLAST search failed: {e}"
        )


@router.post("/search/antibody", response_model=BlastSearchResponse)
async def analyze_antibody_sequence(request: BlastSearchRequest):
    """Analyze antibody sequences using IgBLAST"""
    try:
        if not request.organism:
            raise HTTPException(
                status_code=400,
                detail="Organism is required for antibody analysis",
            )

        igblast_service = IgBlastService()

        results = igblast_service.analyze_antibody_sequence(
            query_sequence=request.query_sequence,
            organism=request.organism,
            blast_type=request.blast_type,
            evalue=request.evalue,
        )

        # Get additional analysis
        summary = igblast_service.get_antibody_summary(results)
        cdr3_info = igblast_service.extract_cdr3(results)
        gene_assignments = igblast_service.get_gene_assignments(results)

        return BlastSearchResponse(
            success=True,
            message=f"Antibody analysis completed successfully",
            data={
                "results": results,
                "summary": summary,
                "cdr3_info": cdr3_info,
                "gene_assignments": gene_assignments,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Antibody analysis failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Antibody analysis failed: {e}"
        )


@router.post("/database/create", response_model=BlastSearchResponse)
async def create_custom_database(request: CustomDatabaseRequest):
    """Create a custom BLAST database"""
    try:
        blast_service = BlastService()

        result = blast_service.create_custom_database(
            sequences=request.sequences,
            database_name=request.database_name,
            database_type=request.database_type,
        )

        return BlastSearchResponse(
            success=True,
            message=f"Custom database '{request.database_name}' created successfully",
            data={"database": result},
        )
    except Exception as e:
        logger.error(f"Database creation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Database creation failed: {e}"
        )


@router.post("/upload", response_model=BlastSearchResponse)
async def upload_sequences_for_blast(
    file: Optional[UploadFile] = File(None),
    sequences: Optional[str] = Form(None),
):
    """Upload sequences for BLAST analysis"""
    try:
        if file:
            if not file.filename.endswith((".fasta", ".fa", ".txt")):
                raise HTTPException(
                    status_code=400, detail="File must be FASTA format"
                )
            content = await file.read()
            sequence_text = content.decode("utf-8")
        elif sequences:
            sequence_text = sequences
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or sequences must be provided",
            )

        # Validate sequence
        blast_service = BlastService()
        is_valid = blast_service.validate_sequence(
            sequence_text, "protein"
        )  # Default to protein

        if not is_valid:
            raise HTTPException(
                status_code=400, detail="Invalid sequence format"
            )

        return BlastSearchResponse(
            success=True,
            message="Sequences uploaded successfully",
            data={"sequence": sequence_text, "valid": True},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.get("/organisms")
async def get_supported_organisms():
    """Get list of supported organisms for IgBLAST"""
    try:
        igblast_service = IgBlastService()
        organisms = igblast_service.get_supported_organisms()

        return BlastSearchResponse(
            success=True,
            message="Supported organisms retrieved successfully",
            data={"organisms": organisms},
        )
    except Exception as e:
        logger.error(f"Failed to get organisms: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get organisms: {e}"
        )


@router.get("/job/{job_id}")
async def get_blast_job_status(job_id: str):
    """Get status of a BLAST job"""
    try:
        blast_service = BlastService()
        status = blast_service.get_job_status(job_id)

        if not status:
            raise HTTPException(status_code=404, detail="Job not found")

        return BlastSearchResponse(
            success=True,
            message="Job status retrieved successfully",
            data={"job": status},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get job status: {e}"
        )
