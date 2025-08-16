from typing import Optional
from fastapi import APIRouter, HTTPException, File, Form, UploadFile

from backend.models.models import MSACreationRequest, MSAAnnotationRequest
from backend.models.models_v2 import AnnotationResult as V2AnnotationResult
from backend.models.requests_v2 import AnnotationRequestV2
from backend.services import AnnotationService, MSAService, JobService
from backend.logger import logger

router = APIRouter()


@router.get("/health")
async def health_check_v2():
    return {"status": "healthy"}


@router.post("/annotate", response_model=V2AnnotationResult)
async def annotate_sequences_v2(request: AnnotationRequestV2):
    try:
        annotation_service = AnnotationService()
        return annotation_service.process_annotation_request(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


@router.post("/msa-viewer/upload")
async def upload_msa_sequences_v2(
    file: Optional[UploadFile] = File(None),
    sequences: Optional[str] = Form(None),
):
    """Upload sequences for MSA analysis"""
    try:
        msa_service = MSAService()
        sequence_inputs, errors = await msa_service.process_upload(
            file, sequences
        )

        return {
            "success": True,
            "message": f"Successfully uploaded {len(sequence_inputs)} sequences for MSA",
            "data": {
                "sequences": [seq.model_dump() for seq in sequence_inputs],
                "validation_errors": errors,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MSA upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"MSA upload failed: {e}")


@router.post("/msa-viewer/create-msa")
async def create_msa_v2(request: MSACreationRequest):
    """Create multiple sequence alignment"""
    try:
        msa_service = MSAService()
        return msa_service.create_msa(request)
    except Exception as e:
        logger.error(f"MSA creation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"MSA creation failed: {e}"
        )


@router.post("/msa-viewer/annotate-msa")
async def annotate_msa_v2(request: MSAAnnotationRequest):
    """Annotate sequences in MSA"""
    try:
        job_service = JobService()
        job_id = job_service.create_annotation_job(request)

        return {
            "success": True,
            "message": "MSA annotation job created",
            "data": {"job_id": job_id, "status": "pending"},
        }
    except Exception as e:
        logger.error(f"MSA annotation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"MSA annotation failed: {e}"
        )


@router.get("/msa-viewer/job/{job_id}")
async def get_job_status_v2(job_id: str):
    """Get status of a background job"""
    try:
        job_service = JobService()
        job_status = job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "success": True,
            "message": "Job status retrieved successfully",
            "data": job_status,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get job status: {e}"
        )


@router.get("/msa-viewer/jobs")
async def list_jobs_v2():
    """List all jobs"""
    try:
        job_service = JobService()
        jobs = job_service.list_jobs()

        return {
            "success": True,
            "message": f"Retrieved {len(jobs)} jobs",
            "data": {"jobs": jobs},
        }
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list jobs: {e}"
        )
