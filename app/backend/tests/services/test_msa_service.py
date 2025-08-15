import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, UploadFile
from io import BytesIO

from backend.models.models import MSACreationRequest, SequenceInput
from backend.services.msa_service import MSAService


@pytest.fixture
def msa_service():
    return MSAService()


@pytest.fixture
def mock_file():
    content = b">seq1\nACGT\n>seq2\nGCTA"
    return UploadFile(
        filename="test.fasta",
        file=BytesIO(content)
    )


@pytest.fixture
def mock_sequences():
    return ">seq1\nACGT\n>seq2\nGCTA"


@pytest.fixture
def mock_msa_request():
    return MSACreationRequest(
        sequences=[
            SequenceInput(name="seq1", heavy_chain="ACGT"),
            SequenceInput(name="seq2", heavy_chain="GCTA")
        ],
        alignment_method="clustal",
        numbering_scheme="imgt"
    )


@pytest.mark.asyncio
async def test_get_fasta_content_from_file(msa_service, mock_file):
    content = await msa_service._get_fasta_content(mock_file, None)
    assert ">seq1" in content
    assert "ACGT" in content
    assert ">seq2" in content
    assert "GCTA" in content


@pytest.mark.asyncio
async def test_get_fasta_content_from_sequences(msa_service, mock_sequences):
    content = await msa_service._get_fasta_content(None, mock_sequences)
    assert content == mock_sequences


@pytest.mark.asyncio
async def test_get_fasta_content_invalid_file_type(msa_service):
    invalid_file = UploadFile(filename="test.txt", file=BytesIO(b"invalid"))
    with pytest.raises(HTTPException) as exc:
        await msa_service._get_fasta_content(invalid_file, None)
    assert exc.value.status_code == 400
    assert "File must be FASTA format" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_get_fasta_content_no_input(msa_service):
    with pytest.raises(HTTPException) as exc:
        await msa_service._get_fasta_content(None, None)
    assert exc.value.status_code == 400
    assert "Either file or sequences must be provided" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_process_upload_valid_fasta(msa_service, mock_file):
    with patch('backend.annotation.sequence_processor.SequenceProcessor') as mock_processor:
        mock_processor.return_value.parse_fasta.return_value = [
            Mock(id="seq1", seq="ACGT"),
            Mock(id="seq2", seq="GCTA")
        ]
        mock_processor.return_value.validate_sequences.return_value = (
            ["ACGT", "GCTA"],
            []
        )
        
        sequence_inputs, errors = await msa_service.process_upload(mock_file, None)
        
        assert len(sequence_inputs) == 2
        assert sequence_inputs[0].name == "seq1"
        assert sequence_inputs[0].heavy_chain == "ACGT"
        assert not errors


@pytest.mark.asyncio
async def test_process_upload_invalid_fasta(msa_service, mock_file):
    with patch('backend.annotation.sequence_processor.SequenceProcessor') as mock_processor:
        mock_processor.return_value.parse_fasta.side_effect = ValueError("Invalid FASTA")
        
        with pytest.raises(HTTPException) as exc:
            await msa_service.process_upload(mock_file, None)
        
        assert exc.value.status_code == 400
        assert "Invalid FASTA format" in str(exc.value.detail)


def test_create_msa_background_job(msa_service, mock_msa_request):
    with patch('backend.jobs.job_manager.job_manager') as mock_manager:
        mock_manager.create_msa_job.return_value = "job123"
        
        # Force background processing by adding more sequences
        for i in range(20):
            mock_msa_request.sequences.append(
                SequenceInput(name=f"seq{i}", heavy_chain="ACGT")
            )
        
        result = msa_service.create_msa(mock_msa_request)
        
        assert result["success"] is True
        assert result["data"]["job_id"] == "job123"
        assert result["data"]["use_background"] is True


def test_create_msa_immediate(msa_service, mock_msa_request):
    with patch('backend.msa.msa_engine.MSAEngine') as mock_msa_engine, \
         patch('backend.msa.msa_annotation.MSAAnnotationEngine') as mock_annotation_engine:
        
        mock_msa_result = Mock(
            metadata={"pssm_data": {"conservation_scores": [], "quality_scores": []}},
            consensus="consensus",
            model_dump=lambda: {}
        )
        mock_annotation_result = Mock(model_dump=lambda: {})
        
        mock_msa_engine.return_value.create_msa.return_value = mock_msa_result
        mock_annotation_engine.return_value.annotate_msa.return_value = mock_annotation_result
        
        result = msa_service.create_msa(mock_msa_request)
        
        assert result["success"] is True
        assert result["data"]["use_background"] is False
        assert "msa_result" in result["data"]
        assert "annotation_result" in result["data"]


def test_create_msa_no_sequences(msa_service):
    request = MSACreationRequest(
        sequences=[],
        alignment_method="clustal",
        numbering_scheme="imgt"
    )
    
    with pytest.raises(ValueError) as exc:
        msa_service._create_immediate_msa(request)
    assert "No valid sequences provided" in str(exc.value)
