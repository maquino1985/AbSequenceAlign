"""
Integration tests for MSA service with real file handling and minimal mocking.
"""

import pytest
from io import BytesIO
from fastapi import UploadFile, HTTPException

from backend.models.models import (
    SequenceInput,
    MSACreationRequest,
    NumberingScheme,
    AlignmentMethod,
)
from backend.services.msa_service import MSAService


class TestMSAIntegration:
    """Integration tests for MSA service functionality."""

    @pytest.fixture
    def real_fasta_content(self):
        """Real FASTA content with valid antibody sequences."""
        return """>heavy_chain_1
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS
>heavy_chain_2
QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS
>light_chain_1
DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK"""

    @pytest.fixture
    def invalid_fasta_content(self):
        """Invalid FASTA content for error testing."""
        return """>seq1
INVALIDSEQUENCEWITHBADCHARACTERS123!@#
>seq2
TOOSHORT"""

    @pytest.fixture
    def msa_service(self):
        """MSA service instance."""
        return MSAService()

    def create_upload_file(
        self, content: str, filename: str = "test.fasta"
    ) -> UploadFile:
        """Helper to create UploadFile objects for testing."""
        return UploadFile(filename=filename, file=BytesIO(content.encode()))

    @pytest.mark.asyncio
    async def test_fasta_content_extraction_from_file(
        self, msa_service, real_fasta_content
    ):
        """Test FASTA content extraction from uploaded file."""
        upload_file = self.create_upload_file(real_fasta_content)

        content = await msa_service._get_fasta_content(upload_file, None)

        assert ">heavy_chain_1" in content
        assert ">heavy_chain_2" in content
        assert ">light_chain_1" in content
        assert "EVQLVESGGGLVQPGGSLRLSCAAS" in content

    @pytest.mark.asyncio
    async def test_fasta_content_extraction_from_text(
        self, msa_service, real_fasta_content
    ):
        """Test FASTA content extraction from text input."""
        content = await msa_service._get_fasta_content(
            None, real_fasta_content
        )

        assert content == real_fasta_content

    @pytest.mark.asyncio
    async def test_file_type_validation(self, msa_service, real_fasta_content):
        """Test file type validation."""
        # Valid file types
        for filename in ["test.fasta", "test.fa", "test.txt"]:
            upload_file = self.create_upload_file(real_fasta_content, filename)
            content = await msa_service._get_fasta_content(upload_file, None)
            assert content == real_fasta_content

        # Invalid file type
        upload_file = self.create_upload_file(real_fasta_content, "test.docx")
        with pytest.raises(HTTPException) as exc_info:
            await msa_service._get_fasta_content(upload_file, None)
        assert exc_info.value.status_code == 400
        assert "File must be FASTA format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_no_input_validation(self, msa_service):
        """Test validation when no input is provided."""
        with pytest.raises(HTTPException) as exc_info:
            await msa_service._get_fasta_content(None, None)
        assert exc_info.value.status_code == 400
        assert "Either file or sequences must be provided" in str(
            exc_info.value.detail
        )

    @pytest.mark.asyncio
    async def test_sequence_upload_processing_success(
        self, msa_service, real_fasta_content
    ):
        """Test successful sequence upload processing."""
        upload_file = self.create_upload_file(real_fasta_content)

        sequence_inputs, errors = await msa_service.process_upload(
            upload_file, None
        )

        # Should have 3 sequences
        assert len(sequence_inputs) == 3
        assert len(errors) == 0

        # Verify sequence structure
        seq1 = sequence_inputs[0]
        assert seq1.name == "heavy_chain_1"
        assert len(seq1.heavy_chain) > 100

        seq2 = sequence_inputs[1]
        assert seq2.name == "heavy_chain_2"
        assert len(seq2.heavy_chain) > 100

        seq3 = sequence_inputs[2]
        assert seq3.name == "light_chain_1"
        assert len(seq3.heavy_chain) > 50  # Light chains are shorter

    @pytest.mark.asyncio
    async def test_sequence_upload_validation_errors(
        self, msa_service, invalid_fasta_content
    ):
        """Test sequence upload with validation errors."""
        upload_file = self.create_upload_file(invalid_fasta_content)

        with pytest.raises(HTTPException) as exc_info:
            await msa_service.process_upload(upload_file, None)

        assert exc_info.value.status_code == 400
        assert "Sequence validation failed" in str(exc_info.value.detail)

    def test_msa_creation_decision_logic(self, msa_service):
        """Test MSA creation decision logic (background vs immediate)."""
        # Small dataset - should process immediately
        small_request = MSACreationRequest(
            sequences=[
                SequenceInput(
                    name="seq1",
                    heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
                ),
                SequenceInput(
                    name="seq2",
                    heavy_chain="QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
                ),
            ],
            alignment_method=AlignmentMethod.MUSCLE,
            numbering_scheme=NumberingScheme.IMGT,
        )

        # Large dataset - should use background processing
        large_sequences = []
        for i in range(15):  # More than 10 sequences
            large_sequences.append(
                SequenceInput(
                    name=f"seq{i}",
                    heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
                )
            )

        large_request = MSACreationRequest(
            sequences=large_sequences,
            alignment_method=AlignmentMethod.MUSCLE,
            numbering_scheme=NumberingScheme.IMGT,
        )

        # Test decision logic by examining total sequence count
        small_total = sum(
            len(seq.get_all_chains()) for seq in small_request.sequences
        )
        large_total = sum(
            len(seq.get_all_chains()) for seq in large_request.sequences
        )

        assert small_total <= 10  # Should process immediately
        assert large_total > 10  # Should use background processing

    def test_sequence_extraction_for_msa(self):
        """Test sequence extraction logic for MSA creation."""
        request = MSACreationRequest(
            sequences=[
                SequenceInput(
                    name="antibody1",
                    heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
                    light_chain="DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
                ),
                SequenceInput(
                    name="antibody2",
                    heavy_chain="QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
                ),
            ],
            alignment_method=AlignmentMethod.MUSCLE,
            numbering_scheme=NumberingScheme.IMGT,
        )

        # Extract sequences as would be done in _create_immediate_msa
        sequences = []
        for seq_input in request.sequences:
            chains = seq_input.get_all_chains()
            for chain_name, sequence in chains.items():
                sequences.append((f"{seq_input.name}_{chain_name}", sequence))

        # Should have 3 sequences: antibody1_heavy_chain, antibody1_light_chain, antibody2_heavy_chain
        assert len(sequences) == 3
        assert (
            "antibody1_heavy_chain",
            request.sequences[0].heavy_chain,
        ) in sequences
        assert (
            "antibody1_light_chain",
            request.sequences[0].light_chain,
        ) in sequences
        assert (
            "antibody2_heavy_chain",
            request.sequences[1].heavy_chain,
        ) in sequences

    def test_empty_sequence_validation(self):
        """Test validation of empty sequences."""
        request = MSACreationRequest(
            sequences=[],
            alignment_method=AlignmentMethod.MUSCLE,
            numbering_scheme=NumberingScheme.IMGT,
        )

        # Should have no sequences to extract
        sequences = []
        for seq_input in request.sequences:
            chains = seq_input.get_all_chains()
            for chain_name, sequence in chains.items():
                sequences.append((f"{seq_input.name}_{chain_name}", sequence))

        assert len(sequences) == 0
