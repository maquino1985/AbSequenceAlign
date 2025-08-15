from typing import List, Optional

from backend.annotation.AnarciResultProcessor import AnarciResultProcessor
from backend.annotation.sequence_processor import SequenceProcessor
from backend.jobs.job_manager import job_manager
from backend.logger import logger
from backend.models.models import MSACreationRequest, MSAAnnotationRequest
from backend.models.models_v2 import (
    AnnotationResult as V2AnnotationResult,
    Sequence as V2Sequence,
    Chain as V2Chain,
    Domain as V2Domain,
    Region as V2Region,
    RegionFeature as V2RegionFeature,
    DomainType,
)
from backend.models.requests_v2 import AnnotationRequestV2
from backend.msa.msa_annotation import MSAAnnotationEngine
from backend.msa.msa_engine import MSAEngine
from fastapi import APIRouter, HTTPException, File, Form, UploadFile

router = APIRouter()


@router.get("/health")
async def health_check_v2():
    return {"status": "healthy"}


@router.post("/annotate", response_model=V2AnnotationResult)
async def annotate_sequences_v2(request: AnnotationRequestV2):
    try:
        # Build input for processor (reuse existing logic)
        input_dict = {}
        for seq in request.sequences:
            chains = seq.get_all_chains()
            if chains:
                input_dict[seq.name] = chains

        processor = AnarciResultProcessor(
            input_dict, numbering_scheme=request.numbering_scheme.value
        )

        v2_sequences: List[V2Sequence] = []
        for result in processor.results:
            v2_chains: List[V2Chain] = []
            for chain in result.chains:
                v2_domains: List[V2Domain] = []
                for domain in chain.domains:
                    # Map domain type
                    if getattr(domain, "domain_type", "V") == "C":
                        dtype = DomainType.CONSTANT
                    elif getattr(domain, "domain_type", "V") == "LINKER":
                        dtype = DomainType.LINKER
                    else:
                        dtype = DomainType.VARIABLE

                    # Absolute start/stop for domain
                    dstart = None
                    dstop = None
                    if domain.alignment_details:
                        if dtype == DomainType.LINKER:
                            dstart = domain.alignment_details.get("start")
                            dstop = domain.alignment_details.get("end")
                        else:
                            dstart = domain.alignment_details.get(
                                "query_start"
                            )
                            dstop = domain.alignment_details.get("query_end")
                    # dstart += 1
                    v2_regions: List[V2Region] = []
                    # Regions if present
                    if hasattr(domain, "regions") and domain.regions:
                        for rname, r in domain.regions.items():
                            # r may be a dataclass-like object or a plain dict
                            if isinstance(r, dict):
                                # Convert 0-based positions to 1-based for frontend
                                start = int(r.get("start")) + 1
                                stop = int(r.get("stop")) + 1
                                seq_val = r.get("sequence")
                            else:
                                # Convert 0-based positions to 1-based for frontend
                                start = int(r.start) + 1
                                stop = int(r.stop) + 1
                                seq_val = r.sequence
                            features = [
                                V2RegionFeature(kind="sequence", value=seq_val)
                            ]
                            v2_regions.append(
                                V2Region(
                                    name=rname,
                                    start=start,
                                    stop=stop,
                                    features=features,
                                )
                            )

                    v2_domains.append(
                        V2Domain(
                            domain_type=dtype,
                            start=dstart,
                            stop=dstop,
                            sequence=domain.sequence,
                            regions=v2_regions,
                            isotype=getattr(domain, "isotype", None),
                            species=getattr(domain, "species", None),
                            metadata={},
                        )
                    )

                v2_chains.append(
                    V2Chain(
                        name=chain.name,
                        sequence=chain.sequence,
                        domains=v2_domains,
                    )
                )

            v2_sequences.append(
                V2Sequence(
                    name=result.biologic_name,
                    original_sequence=(
                        v2_chains[0].sequence if v2_chains else ""
                    ),
                    chains=v2_chains,
                )
            )

        # Calculate statistics like v1
        chain_types = {}
        isotypes = {}
        species_counts = {}

        for result in processor.results:
            for chain in result.chains:
                # Get the primary domain (first variable domain) for chain metadata
                primary_domain = next(
                    (d for d in chain.domains if d.domain_type == "V"),
                    chain.domains[0],
                )

                # Stats - only count primary domain
                if primary_domain.isotype:
                    chain_types[primary_domain.isotype] = (
                        chain_types.get(primary_domain.isotype, 0) + 1
                    )
                    isotypes[primary_domain.isotype] = (
                        isotypes.get(primary_domain.isotype, 0) + 1
                    )
                if primary_domain.species:
                    species_counts[primary_domain.species] = (
                        species_counts.get(primary_domain.species, 0) + 1
                    )

        return V2AnnotationResult(
            sequences=v2_sequences,
            numbering_scheme=request.numbering_scheme.value,
            total_sequences=len(v2_sequences),
            chain_types=chain_types,
            isotypes=isotypes,
            species=species_counts,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


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
