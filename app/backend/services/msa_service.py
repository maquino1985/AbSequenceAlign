from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException

from backend.models.models import SequenceInput, MSACreationRequest
from backend.annotation.sequence_processor import SequenceProcessor
from backend.msa.msa_engine import MSAEngine
from backend.msa.msa_annotation import MSAAnnotationEngine
from backend.jobs.job_manager import job_manager
from backend.logger import logger


class MSAService:
    def __init__(self):
        self.sequence_processor = SequenceProcessor()
        self.msa_engine = MSAEngine()
        self.annotation_engine = MSAAnnotationEngine()

    async def process_upload(
        self, file: Optional[UploadFile], sequences: Optional[str]
    ) -> Tuple[List[SequenceInput], List[str]]:
        """Process uploaded sequences and return sequence inputs and validation errors"""
        fasta_content = await self._get_fasta_content(file, sequences)

        try:
            records = self.sequence_processor.parse_fasta(fasta_content)
            sequences_list = [str(record.seq) for record in records]
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid FASTA format: {e}"
            )

        valid_sequences, errors = self.sequence_processor.validate_sequences(
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
            seq_input = SequenceInput(
                name=record.id or f"Sequence_{i + 1}",
                heavy_chain=seq,  # Assume heavy chain for now
            )
            sequence_inputs.append(seq_input)

        return sequence_inputs, errors

    async def _get_fasta_content(
        self, file: Optional[UploadFile], sequences: Optional[str]
    ) -> str:
        """Extract FASTA content from either file upload or direct sequence input"""
        if file:
            if not file.filename.endswith((".fasta", ".fa", ".txt")):
                raise HTTPException(
                    status_code=400, detail="File must be FASTA format"
                )
            content = await file.read()
            return content.decode("utf-8")
        elif sequences:
            return sequences
        else:
            raise HTTPException(
                status_code=400,
                detail="Either file or sequences must be provided",
            )

    def create_msa(self, request: MSACreationRequest) -> dict:
        """Create multiple sequence alignment"""
        total_sequences = sum(
            len(seq_input.get_all_chains()) for seq_input in request.sequences
        )
        use_background = (
            total_sequences > 10
        )  # Use background for >10 sequences

        if use_background:
            return self._create_background_msa_job(request, total_sequences)
        else:
            return self._create_immediate_msa(request)

    def _create_background_msa_job(
        self, request: MSACreationRequest, total_sequences: int
    ) -> dict:
        """Create a background job for MSA creation"""
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

    def _create_immediate_msa(self, request: MSACreationRequest) -> dict:
        """Create MSA immediately for small datasets"""
        # Extract sequences
        sequences = []
        for seq_input in request.sequences:
            chains = seq_input.get_all_chains()
            for chain_name, sequence in chains.items():
                sequences.append((f"{seq_input.name}_{chain_name}", sequence))

        if not sequences:
            raise ValueError("No valid sequences provided")

        # Create MSA
        msa_result = self.msa_engine.create_msa(
            sequences=sequences, method=request.alignment_method
        )

        # Annotate sequences
        annotation_result = self.annotation_engine.annotate_msa(
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
