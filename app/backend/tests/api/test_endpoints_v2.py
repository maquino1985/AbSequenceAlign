import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.api.v2.endpoints import router
from backend.models.models import MSACreationRequest, MSAAnnotationRequest
from backend.models.models_v2 import AnnotationResult as V2AnnotationResult
from backend.models.requests_v2 import AnnotationRequestV2, InputSequence


@pytest.fixture
def client():
    return TestClient(router)


@pytest.fixture
def mock_annotation_request():
    return AnnotationRequestV2(
        sequences=[
            InputSequence(
                name="test",
                heavy_chain="SEQUENCE"
            )
        ],
        numbering_scheme="imgt"
    )


@pytest.fixture
def mock_msa_request():
    return MSACreationRequest(
        sequences=[
            InputSequence(
                name="test",
                heavy_chain="SEQUENCE"
            )
        ],
        alignment_method="clustal",
        numbering_scheme="imgt"
    )


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch('backend.services.annotation_service.AnnotationService')
def test_annotate_sequences_success(mock_service_cls, client, mock_annotation_request):
    mock_result = V2AnnotationResult(
        sequences=[],
        numbering_scheme="imgt",
        total_sequences=0,
        chain_types={},
        isotypes={},
        species={}
    )
    mock_service_cls.return_value.process_annotation_request.return_value = mock_result
    
    response = client.post("/annotate", json=mock_annotation_request.model_dump())
    
    assert response.status_code == 200
    assert response.json() == mock_result.model_dump()


@patch('backend.services.annotation_service.AnnotationService')
def test_annotate_sequences_error(mock_service_cls, client, mock_annotation_request):
    mock_service_cls.return_value.process_annotation_request.side_effect = Exception("Test error")
    
    response = client.post("/annotate", json=mock_annotation_request.model_dump())
    
    assert response.status_code == 500
    assert "Annotation failed" in response.json()["detail"]


@patch('backend.services.msa_service.MSAService')
def test_upload_msa_sequences_success(mock_service_cls, client):
    mock_inputs = [
        InputSequence(name="test", heavy_chain="SEQUENCE")
    ]
    mock_service_cls.return_value.process_upload.return_value = (mock_inputs, [])
    
    response = client.post(
        "/msa-viewer/upload",
        files={"file": ("test.fasta", b">test\nSEQUENCE")}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]["sequences"]) == 1


@patch('backend.services.msa_service.MSAService')
def test_create_msa_success(mock_service_cls, client, mock_msa_request):
    mock_result = {
        "success": True,
        "data": {
            "job_id": "test_job",
            "use_background": True
        }
    }
    mock_service_cls.return_value.create_msa.return_value = mock_result
    
    response = client.post("/msa-viewer/create-msa", json=mock_msa_request.model_dump())
    
    assert response.status_code == 200
    assert response.json() == mock_result


@patch('backend.services.job_service.JobService')
def test_annotate_msa_success(mock_service_cls, client):
    mock_service_cls.return_value.create_annotation_job.return_value = "test_job"
    
    request = MSAAnnotationRequest(
        msa_result={},
        numbering_scheme="imgt"
    )
    
    response = client.post("/msa-viewer/annotate-msa", json=request.model_dump())
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["job_id"] == "test_job"


@patch('backend.services.job_service.JobService')
def test_get_job_status_success(mock_service_cls, client):
    mock_service_cls.return_value.get_job_status.return_value = {
        "id": "test_job",
        "status": "completed"
    }
    
    response = client.get("/msa-viewer/job/test_job")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "completed"


@patch('backend.services.job_service.JobService')
def test_get_job_status_not_found(mock_service_cls, client):
    mock_service_cls.return_value.get_job_status.return_value = None
    
    response = client.get("/msa-viewer/job/nonexistent")
    
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]


@patch('backend.services.job_service.JobService')
def test_list_jobs_success(mock_service_cls, client):
    mock_service_cls.return_value.list_jobs.return_value = [
        {"id": "job1", "status": "completed"},
        {"id": "job2", "status": "pending"}
    ]
    
    response = client.get("/msa-viewer/jobs")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]["jobs"]) == 2
