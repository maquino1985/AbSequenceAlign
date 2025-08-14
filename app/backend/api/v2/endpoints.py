"""
Simple API endpoints for v2 API.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from backend.models.models import MSACreationRequest, MSAAnnotationRequest
from backend.models.requests_v2 import AnnotationRequestV2
from backend.msa.msa_engine import MSAEngine
from backend.msa.msa_annotation import MSAAnnotationEngine
from backend.annotation.anarci_result_processor import AnarciResultProcessor
from backend.core.constants import NumberingScheme
from backend.logger import logger

router = APIRouter()


@router.get("/health")
async def health_check_v2():
    """Health check endpoint"""
    return {"status": "healthy", "version": "v2"}


@router.get("/")
async def root_v2():
    """Root endpoint"""
    return {"message": "AbSequenceAlign API v2", "status": "operational"}


@router.post("/annotate")
async def annotate_sequences_v2(request: AnnotationRequestV2):
    """Annotate sequences using the v2 API"""
    try:
        # Convert request to the format expected by AnarciResultProcessor
        sequences_dict = {}
        for seq in request.sequences:
            chains = seq.get_all_chains()
            if chains:
                sequences_dict[seq.name] = chains

        if not sequences_dict:
            raise HTTPException(status_code=400, detail="No valid sequences provided")

        # Process sequences using AnarciResultProcessor
        processor = AnarciResultProcessor(
            sequences_dict, 
            numbering_scheme=request.numbering_scheme.value
        )
        
        # Get the results - this is a list of AnarciResultObject instances
        results = processor.results
        
        # Format the response to match the expected structure
        formatted_results = []
        for result_obj in results:
            formatted_results.append({
                "name": result_obj.biologic_name,
                "success": True,
                "data": {
                    "sequence": {
                        "name": result_obj.biologic_name,
                        "chains": [chain.model_dump() for chain in result_obj.chains],
                        "isotype": None  # Will be set per chain if available
                    }
                }
            })

        # Return the response structure that matches both test files
        return {
            "success": True,
            "message": "Workflow completed",
            "data": {
                "results": formatted_results,
                "summary": {
                    "total": len(formatted_results),
                    "successful": len(formatted_results),
                    "failed": 0
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Annotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


@router.post("/msa-viewer/create-msa")
async def create_msa_v2(request: MSACreationRequest):
    """Create multiple sequence alignment using v2 API"""
    try:
        from backend.jobs.job_manager import job_manager
        
        # Extract sequences
        sequences = []
        for seq_input in request.sequences:
            chains = seq_input.get_all_chains()
            for chain_name, sequence in chains.items():
                sequences.append(
                    (f"{seq_input.name}_{chain_name}", sequence)
                )

        if not sequences:
            raise HTTPException(status_code=400, detail="No valid sequences provided")

        # Create MSA
        msa_engine = MSAEngine()
        msa_result = msa_engine.create_msa(
            sequences=sequences, 
            method=request.alignment_method
        )

        # Annotate sequences
        annotation_engine = MSAAnnotationEngine()
        annotation_result = annotation_engine.annotate_msa(
            msa_result=msa_result,
            numbering_scheme=request.numbering_scheme,
        )

        # Extract PSSM data from metadata
        pssm_data = msa_result.metadata.get("pssm_data", {})

        return {
            "success": True,
            "message": f"Successfully created MSA for {len(sequences)} sequences with enhanced features",
            "data": {
                "msa_result": msa_result.model_dump(),
                "annotation_result": annotation_result.model_dump(),
                "pssm_data": pssm_data,
                "consensus": msa_result.consensus,
                "conservation_scores": pssm_data.get("conservation_scores", []),
                "quality_scores": pssm_data.get("quality_scores", []),
                "use_background": False,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MSA creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"MSA creation failed: {e}")


@router.post("/msa-viewer/annotate-msa")
async def annotate_msa_v2(request: MSAAnnotationRequest):
    """Annotate sequences in MSA using v2 API"""
    try:
        from backend.jobs.job_manager import job_manager
        
        # Create a background job for annotation
        job_id = job_manager.create_annotation_job(request)

        return {
            "success": True,
            "message": "MSA annotation job created",
            "data": {"job_id": job_id, "status": "pending"},
        }
    except Exception as e:
        logger.error(f"MSA annotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"MSA annotation failed: {e}")
