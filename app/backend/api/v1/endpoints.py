from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from backend.annotation.alignment_engine import AlignmentEngine
from backend.annotation.annotation_engine import annotate_sequences_with_processor
from backend.annotation.sequence_processor import SequenceProcessor
from backend.data_store import data_store
from backend.logger import logger
from backend.models.models import (
    AlignmentRequest, AnnotationRequest,
    APIResponse, AlignmentResult, SequenceInput,
    MSACreationRequest, MSAAnnotationRequest, MSAJobStatus
)
from backend.jobs.job_manager import job_manager

router = APIRouter()

sequence_processor = SequenceProcessor()
alignment_engine = AlignmentEngine()


@router.get("/")
async def root():
    return {
        "message": "AbSequenceAlign API",
        "version": "0.1.0",
        "status": "running"
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/upload", response_model=APIResponse)
async def upload_sequences(
        file: Optional[UploadFile] = File(None),
        sequences: Optional[str] = Form(None)
):
    try:
        fasta_content = ""
        if file:
            if not file.filename.endswith((".fasta", ".fa", ".txt")):
                raise HTTPException(status_code=400, detail="File must be FASTA format")
            fasta_content = await file.read()
            fasta_content = fasta_content.decode('utf-8')
        elif sequences:
            fasta_content = sequences
        else:
            raise HTTPException(status_code=400, detail="Either file or sequences must be provided")
        try:
            records = sequence_processor.parse_fasta(fasta_content)
            sequences_list = [str(record.seq) for record in records]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid FASTA format: {e}")
        valid_sequences, errors = sequence_processor.validate_sequences(sequences_list)
        if not valid_sequences:
            raise HTTPException(status_code=400, detail=f"Sequence validation failed: {'; '.join(errors)}")
        if errors:
            logger.warning(f"Some sequences had validation issues: {'; '.join(errors)}")
        dataset_id = data_store.create_dataset(valid_sequences)
        stats = sequence_processor.get_sequence_statistics(valid_sequences)
        return APIResponse(
            success=True,
            message=f"Successfully uploaded {len(valid_sequences)} sequences",
            data={
                "dataset_id": dataset_id,
                "statistics": stats,
                "validation_errors": errors
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.post("/annotate", response_model=APIResponse)
async def annotate_sequences(request: AnnotationRequest):
    try:
        # Extract all sequences from the explicit structure
        sequence_strings = []
        for seq_input in request.sequences:
            # Get all chains using the explicit method
            chain_data = seq_input.get_all_chains()
            sequence_strings.extend(chain_data.values())
        
        valid_sequences, errors = sequence_processor.validate_sequences(sequence_strings)
        if not valid_sequences:
            raise HTTPException(status_code=400, detail=f"Sequence validation failed: {'; '.join(errors)}")
        
        # If validation passes, use the original request.sequences directly
        annotation_result = annotate_sequences_with_processor(
            sequences=request.sequences,
            numbering_scheme=request.numbering_scheme
        )
        return APIResponse(
            success=True,
            message=f"Successfully annotated {annotation_result.total_sequences} sequences",
            data={
                "annotation_result": annotation_result.model_dump(),
                "statistics": {
                    "chain_types": annotation_result.chain_types,
                    "isotypes": annotation_result.isotypes,
                    "species": annotation_result.species
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Annotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


@router.post("/align", response_model=APIResponse)
async def align_sequences(request: AlignmentRequest):
    try:
        sequences = data_store.get_sequences(request.dataset_id)
        if not sequences:
            raise HTTPException(status_code=404, detail="Dataset not found")
        alignment_result = alignment_engine.align_sequences(
            sequences=sequences,
            method=request.method,
            numbering_scheme=request.numbering_scheme,
            gap_open=request.gap_open,
            gap_extend=request.gap_extend,
            matrix=request.matrix
        )
        result = AlignmentResult(
            dataset_id=request.dataset_id,
            method=request.method,
            alignment=alignment_result["alignment"],
            statistics=alignment_result,
            numbering_scheme=request.numbering_scheme
        )
        data_store.store_alignment_result(request.dataset_id, result)
        return APIResponse(
            success=True,
            message=f"Successfully aligned {len(sequences)} sequences using {request.method.value}",
            data={
                "alignment_result": result.dict(),
                "statistics": alignment_result
            }
        )
    except Exception as e:
        logger.error(f"Alignment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Alignment failed: {e}")


@router.get("/alignment/{dataset_id}")
async def get_alignment(dataset_id: str):
    try:
        alignment_result = data_store.get_alignment_result(dataset_id)
        if not alignment_result:
            raise HTTPException(status_code=404, detail="Alignment not found")
        return APIResponse(
            success=True,
            message="Alignment retrieved successfully",
            data=alignment_result.dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve alignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alignment: {e}")


@router.get("/dataset/{dataset_id}")
async def get_dataset(dataset_id: str):
    try:
        dataset_info = data_store.get_dataset_info(dataset_id)
        if not dataset_info:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return APIResponse(
            success=True,
            message="Dataset retrieved successfully",
            data=dataset_info.dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dataset: {e}")


@router.get("/datasets")
async def list_datasets():
    try:
        datasets = data_store.list_datasets()
        stats = data_store.get_dataset_statistics()
        return APIResponse(
            success=True,
            message=f"Retrieved {len(datasets)} datasets",
            data={
                "datasets": [dataset.dict() for dataset in datasets],
                "statistics": stats
            }
        )
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {e}")


@router.delete("/dataset/{dataset_id}")
async def delete_dataset(dataset_id: str):
    try:
        success = data_store.delete_dataset(dataset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return APIResponse(
            success=True,
            message=f"Dataset {dataset_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dataset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {e}")


# MSA Viewer Endpoints

@router.post("/msa-viewer/upload", response_model=APIResponse)
async def upload_msa_sequences(
    file: Optional[UploadFile] = File(None),
    sequences: Optional[str] = Form(None)
):
    """Upload sequences for MSA analysis"""
    try:
        fasta_content = ""
        if file:
            if not file.filename.endswith((".fasta", ".fa", ".txt")):
                raise HTTPException(status_code=400, detail="File must be FASTA format")
            fasta_content = await file.read()
            fasta_content = fasta_content.decode('utf-8')
        elif sequences:
            fasta_content = sequences
        else:
            raise HTTPException(status_code=400, detail="Either file or sequences must be provided")
        
        try:
            records = sequence_processor.parse_fasta(fasta_content)
            sequences_list = [str(record.seq) for record in records]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid FASTA format: {e}")
        
        valid_sequences, errors = sequence_processor.validate_sequences(sequences_list)
        if not valid_sequences:
            raise HTTPException(status_code=400, detail=f"Sequence validation failed: {'; '.join(errors)}")
        
        if errors:
            logger.warning(f"Some sequences had validation issues: {'; '.join(errors)}")
        
        # Create SequenceInput objects
        sequence_inputs = []
        for i, (record, seq) in enumerate(zip(records, valid_sequences)):
            seq_input = SequenceInput(
                name=record.id or f"Sequence_{i+1}",
                heavy_chain=seq  # Assume heavy chain for now
            )
            sequence_inputs.append(seq_input)
        
        return APIResponse(
            success=True,
            message=f"Successfully uploaded {len(valid_sequences)} sequences for MSA",
            data={
                "sequences": [seq.model_dump() for seq in sequence_inputs],
                "validation_errors": errors
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MSA upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"MSA upload failed: {e}")


@router.post("/msa-viewer/create-msa", response_model=APIResponse)
async def create_msa(request: MSACreationRequest):
    """Create multiple sequence alignment"""
    try:
        # Determine if we should use background processing
        total_sequences = sum(len(seq_input.get_all_chains()) for seq_input in request.sequences)
        use_background = total_sequences > 10  # Use background for >10 sequences
        
        if use_background:
            # Create background job
            job_id = job_manager.create_msa_job(request)
            return APIResponse(
                success=True,
                message=f"MSA job created for {total_sequences} sequences",
                data={
                    "job_id": job_id,
                    "status": "pending",
                    "use_background": True
                }
            )
        else:
            # Process immediately for small datasets
            from backend.msa.msa_engine import MSAEngine
            from backend.msa.msa_annotation import MSAAnnotationEngine
            
            msa_engine = MSAEngine()
            annotation_engine = MSAAnnotationEngine()
            
            # Extract sequences
            sequences = []
            for seq_input in request.sequences:
                chains = seq_input.get_all_chains()
                for chain_name, sequence in chains.items():
                    sequences.append((f"{seq_input.name}_{chain_name}", sequence))
            
            if not sequences:
                raise ValueError("No valid sequences provided")
            
            # Create MSA
            msa_result = msa_engine.create_msa(
                sequences=sequences,
                method=request.alignment_method
            )
            
            # Annotate sequences
            annotation_result = annotation_engine.annotate_msa(
                msa_result=msa_result,
                numbering_scheme=request.numbering_scheme
            )
            
            return APIResponse(
                success=True,
                message=f"Successfully created MSA for {len(sequences)} sequences",
                data={
                    "msa_result": msa_result.model_dump(),
                    "annotation_result": annotation_result.model_dump(),
                    "use_background": False
                }
            )
            
    except Exception as e:
        logger.error(f"MSA creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"MSA creation failed: {e}")


@router.post("/msa-viewer/annotate-msa", response_model=APIResponse)
async def annotate_msa(request: MSAAnnotationRequest):
    """Annotate sequences in MSA"""
    try:
        # For now, create a background job for annotation
        job_id = job_manager.create_annotation_job(request)
        
        return APIResponse(
            success=True,
            message="MSA annotation job created",
            data={
                "job_id": job_id,
                "status": "pending"
            }
        )
    except Exception as e:
        logger.error(f"MSA annotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"MSA annotation failed: {e}")


@router.get("/msa-viewer/job/{job_id}", response_model=APIResponse)
async def get_job_status(job_id: str):
    """Get status of a background job"""
    try:
        job_status = job_manager.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return APIResponse(
            success=True,
            message="Job status retrieved successfully",
            data=job_status.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {e}")


@router.get("/msa-viewer/jobs", response_model=APIResponse)
async def list_jobs():
    """List all jobs"""
    try:
        # Get all jobs from job manager
        jobs = []
        for job_id, job_status in job_manager.jobs.items():
            jobs.append(job_status.model_dump())
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(jobs)} jobs",
            data={"jobs": jobs}
        )
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {e}")
