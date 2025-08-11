from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.annotation.sequence_processor import SequenceProcessor
from backend.database.engine import get_db_session
from backend.jobs.job_manager import job_manager
from backend.logger import logger
from backend.models.models import MSACreationRequest, MSAAnnotationRequest
from backend.models.biologic_models import BiologicResponse
from backend.models.requests_v2 import AnnotationRequestV2
from backend.models.models_v2 import AnnotationResultV2
from backend.msa.msa_annotation import MSAAnnotationEngine
from backend.msa.msa_engine import MSAEngine
from fastapi import APIRouter, HTTPException, File, Form, UploadFile, Depends

router = APIRouter()


@router.get("/health")
async def health_check_v2():
    return {"status": "healthy"}


@router.post("/annotate")
async def annotate_sequences_v2(
    request: AnnotationRequestV2,
    persist_to_database: bool = True,
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        # Use the command pattern for clean separation of concerns
        from backend.application.commands import ProcessAnnotationCommand
        from backend.application.handlers import WorkflowHandler
        from backend.application.services.annotation_service import (
            AnnotationService,
        )
        from backend.application.services.validation_service import (
            ValidationService,
        )
        from backend.application.services.response_service import (
            ResponseService,
        )
        from backend.application.services.biologic_service import (
            BiologicService,
        )

        # Convert request sequences to the format expected by the service
        input_dict = {}
        for seq in request.sequences:
            chain_data = seq.get_all_chains()
            if chain_data:
                input_dict[seq.name] = chain_data

        # Create command and handler
        command = ProcessAnnotationCommand(
            {
                "sequences": input_dict,
                "numbering_scheme": request.numbering_scheme.value,
                "persist_to_database": persist_to_database,
            }
        )

        handler = WorkflowHandler(
            annotation_service=AnnotationService(),
            validation_service=ValidationService(),
            response_service=ResponseService(),
            biologic_service=BiologicService(),
        )

        # Execute the workflow
        result = await handler.handle(command)
        
        if result["success"]:
            return result["data"]
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


@router.post("/annotate-with-persistence", response_model=dict)
async def annotate_and_persist_sequences_v2(
    request: AnnotationRequestV2,
    organism: Optional[str] = None,
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    Annotate sequences and persist them as biologic entities.

    This endpoint demonstrates the integration pattern:
    1. Use domain entities for annotation (business logic)
    2. Convert to ORM models for persistence
    3. Return Pydantic models for API responses
    """
    try:
        from backend.application.commands import ProcessAnnotationCommand
        from backend.application.handlers import WorkflowHandler
        from backend.application.services.annotation_service import (
            AnnotationService,
        )
        from backend.application.services.validation_service import (
            ValidationService,
        )
        from backend.application.services.response_service import (
            ResponseService,
        )
        from backend.application.services.biologic_service import (
            BiologicService,
        )

        # Convert request sequences to the format expected by the service
        input_dict = {}
        for seq in request.sequences:
            chain_data = seq.get_all_chains()
            if chain_data:
                input_dict[seq.name] = chain_data

        # Create command and handler for persistence workflow
        command = ProcessAnnotationCommand(
            {
                "sequences": input_dict,
                "numbering_scheme": request.numbering_scheme.value,
                "persist_to_database": True,
                "organism": organism,
            }
        )

        handler = WorkflowHandler(
            annotation_service=AnnotationService(),
            validation_service=ValidationService(),
            response_service=ResponseService(),
            biologic_service=BiologicService(),
        )

        # Execute the workflow with persistence
        result = await handler.handle(command)

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Annotation with persistence failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Annotation with persistence failed: {e}"
        )


# Biologic Entity Endpoints
@router.get("/biologics", response_model=list[BiologicResponse])
async def list_biologics_v2(
    skip: int = 0,
    limit: int = 100,
    db_session: AsyncSession = Depends(get_db_session),
):
    """List all biologic entities with pagination."""
    try:
        from backend.application.services.biologic_service import (
            BiologicService,
        )

        biologic_service = BiologicService()
        biologics = await biologic_service.list_biologics(
            db_session=db_session, skip=skip, limit=limit
        )

        return biologics
    except Exception as e:
        logger.error(f"Failed to list biologics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list biologics: {e}"
        )


@router.get("/biologics/{biologic_id}", response_model=BiologicResponse)
async def get_biologic_v2(
    biologic_id: str,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Get a specific biologic entity by ID."""
    try:
        from backend.application.services.biologic_service import (
            BiologicService,
        )
        from backend.core.exceptions import EntityNotFoundError

        biologic_service = BiologicService()
        biologic = await biologic_service.get_biologic(
            db_session=db_session, biologic_id=biologic_id
        )

        return biologic
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get biologic {biologic_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get biologic: {e}"
        )


# MSA Endpoints
@router.post("/msa-viewer/upload")
async def upload_msa_sequences_v2(
    file: Optional[UploadFile] = File(None),
    sequences: Optional[str] = Form(None),
):
    """Upload sequences for MSA analysis"""
    try:
        fasta_content = ""
        if file:
            if not file.filename.endswith((".fasta", ".fa", ".txt")):
                raise HTTPException(
                    status_code=400, detail="File must be FASTA format"
                )
            fasta_content = await file.read()
            fasta_content = fasta_content.decode("utf-8")
        elif sequences:
            fasta_content = sequences
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or sequences must be provided",
            )

        sequence_processor = SequenceProcessor()
        try:
            records = sequence_processor.parse_fasta(fasta_content)
            sequences_list = [str(record.seq) for record in records]
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid FASTA format: {e}"
            )

        valid_sequences, errors = sequence_processor.validate_sequences(
            sequences_list
        )
        if not valid_sequences:
            raise HTTPException(
                status_code=400,
                detail=f"Sequence validation failed: {'; '.join(errors)}",
            )

        if errors:
            logger.warning(
                f"Some sequences had validation issues: {'; '.join(errors)}"
            )

        # Create SequenceInput objects
        sequence_inputs = []
        for i, (record, seq) in enumerate(zip(records, valid_sequences)):
            from backend.models.models import SequenceInput

            seq_input = SequenceInput(
                name=record.id or f"Sequence_{i + 1}",
                heavy_chain=seq,  # Assume heavy chain for now
            )
            sequence_inputs.append(seq_input)

        return {
            "success": True,
            "message": f"Successfully uploaded {len(valid_sequences)} sequences for MSA",
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
        # Determine if we should use background processing
        total_sequences = sum(
            len(seq_input.get_all_chains()) for seq_input in request.sequences
        )
        use_background = (
            total_sequences > 10
        )  # Use background for >10 sequences

        if use_background:
            # Create background job
            job_id = job_manager.create_msa_job(request)
            return {
                "success": True,
                "message": f"MSA job created for {total_sequences} sequences",
                "data": {
                    "job_id": job_id,
                    "status": "pending",
                    "use_background": True,
                },
            }
        else:
            # Process immediately for small datasets
            msa_engine = MSAEngine()
            annotation_engine = MSAAnnotationEngine()

            # Extract sequences
            sequences = []
            for seq_input in request.sequences:
                chains = seq_input.get_all_chains()
                for chain_name, sequence in chains.items():
                    sequences.append(
                        (f"{seq_input.name}_{chain_name}", sequence)
                    )

            if not sequences:
                raise ValueError("No valid sequences provided")

            # Create MSA
            msa_result = msa_engine.create_msa(
                sequences=sequences, method=request.alignment_method
            )

            # Annotate sequences
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
                    "conservation_scores": pssm_data.get(
                        "conservation_scores", []
                    ),
                    "quality_scores": pssm_data.get("quality_scores", []),
                    "use_background": False,
                },
            }

    except Exception as e:
        logger.error(f"MSA creation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"MSA creation failed: {e}"
        )


@router.post("/msa-viewer/annotate-msa")
async def annotate_msa_v2(request: MSAAnnotationRequest):
    """Annotate sequences in MSA"""
    try:
        # For now, create a background job for annotation
        job_id = job_manager.create_annotation_job(request)

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
        job_status = job_manager.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "success": True,
            "message": "Job status retrieved successfully",
            "data": job_status.model_dump(),
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
        # Get all jobs from job manager
        jobs = []
        for job_id, job_status in job_manager.jobs.items():
            jobs.append(job_status.model_dump())

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
