import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Optional

from app.models import (
    UploadRequest, AlignmentRequest, AnnotationRequest,
    APIResponse, DatasetInfo, AlignmentResult, AnnotationResult
)
from app.sequence_processor import SequenceProcessor
from app.annotation_engine import AnnotationEngine
from app.alignment_engine import AlignmentEngine
from app.data_store import data_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AbSequenceAlign API",
    description="Antibody Sequence Alignment and Analysis Tool",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sequence_processor = SequenceProcessor()
annotation_engine = AnnotationEngine()
alignment_engine = AlignmentEngine()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AbSequenceAlign API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/upload", response_model=APIResponse)
async def upload_sequences(
    file: Optional[UploadFile] = File(None),
    sequences: Optional[str] = Form(None)
):
    """
    Upload sequences via FASTA file or raw text
    
    Accepts either:
    - FASTA file upload
    - Raw FASTA text in form data
    """
    try:
        fasta_content = ""
        
        if file:
            # Handle file upload
            if not file.filename.endswith(('.fasta', '.fa', '.txt')):
                raise HTTPException(status_code=400, detail="File must be FASTA format")
            
            fasta_content = await file.read()
            fasta_content = fasta_content.decode('utf-8')
            
        elif sequences:
            # Handle raw FASTA text
            fasta_content = sequences
            
        else:
            raise HTTPException(status_code=400, detail="Either file or sequences must be provided")
        
        # Parse and validate sequences
        try:
            records = sequence_processor.parse_fasta(fasta_content)
            sequences_list = [str(record.seq) for record in records]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid FASTA format: {e}")
        
        # Validate sequences
        valid_sequences, errors = sequence_processor.validate_sequences(sequences_list)
        
        if not valid_sequences:
            raise HTTPException(status_code=400, detail=f"Sequence validation failed: {'; '.join(errors)}")
        
        if errors:
            logger.warning(f"Some sequences had validation issues: {'; '.join(errors)}")
        
        # Create dataset
        dataset_id = data_store.create_dataset(valid_sequences)
        
        # Get statistics
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


@app.post("/annotate", response_model=APIResponse)
async def annotate_sequences(request: AnnotationRequest):
    """
    Annotate sequences with antibody-specific information using ANARCI
    """
    try:
        # Validate sequences
        valid_sequences, errors = sequence_processor.validate_sequences(request.sequences)
        
        if not valid_sequences:
            raise HTTPException(status_code=400, detail=f"Sequence validation failed: {'; '.join(errors)}")
        
        # Annotate sequences
        annotated_sequences = annotation_engine.annotate_sequences(
            sequences=valid_sequences,
            numbering_scheme=request.numbering_scheme,
            chain_type=request.chain_type
        )
        
        # Get annotation statistics
        stats = annotation_engine.get_annotation_statistics(annotated_sequences)
        
        # Create annotation result
        annotation_result = AnnotationResult(
            sequences=annotated_sequences,
            numbering_scheme=request.numbering_scheme,
            total_sequences=len(annotated_sequences),
            chain_types=stats.get("chain_types", {}),
            isotypes=stats.get("isotypes", {}),
            species=stats.get("species", {})
        )
        
        return APIResponse(
            success=True,
            message=f"Successfully annotated {len(annotated_sequences)} sequences",
            data={
                "annotation_result": annotation_result.dict(),
                "statistics": stats
            }
        )
        
    except Exception as e:
        logger.error(f"Annotation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


@app.post("/align", response_model=APIResponse)
async def align_sequences(request: AlignmentRequest):
    """
    Perform sequence alignment using specified method
    """
    try:
        # Get sequences from dataset
        sequences = data_store.get_sequences(request.dataset_id)
        if not sequences:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Perform alignment
        alignment_result = alignment_engine.align_sequences(
            sequences=sequences,
            method=request.method,
            numbering_scheme=request.numbering_scheme,
            gap_open=request.gap_open,
            gap_extend=request.gap_extend,
            matrix=request.matrix
        )
        
        # Create alignment result object
        result = AlignmentResult(
            dataset_id=request.dataset_id,
            method=request.method,
            alignment=alignment_result["alignment"],
            statistics=alignment_result,
            numbering_scheme=request.numbering_scheme
        )
        
        # Store result
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


@app.get("/alignment/{dataset_id}")
async def get_alignment(dataset_id: str):
    """
    Get alignment result for a dataset
    """
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


@app.get("/dataset/{dataset_id}")
async def get_dataset(dataset_id: str):
    """
    Get dataset information
    """
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


@app.get("/datasets")
async def list_datasets():
    """
    List all datasets
    """
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


@app.delete("/dataset/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """
    Delete a dataset and all associated results
    """
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 