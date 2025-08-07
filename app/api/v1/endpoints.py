from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.annotation.alignment_engine import AlignmentEngine
from app.annotation.annotation_engine import annotate_sequences_with_processor
from app.annotation.sequence_processor import SequenceProcessor
from app.data_store import data_store
from app.logger import logger
from app.models.models import (
    AlignmentRequest, AnnotationRequest,
    APIResponse, AlignmentResult, SequenceInput
)

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
