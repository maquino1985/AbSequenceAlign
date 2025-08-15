"""
Integration tests for API endpoints with real request/response handling.
"""

import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from fastapi.exceptions import RequestValidationError
from backend.api.v2.endpoints import router
from backend.models.models import (
    NumberingScheme,
    AlignmentMethod,
    SequenceInput,
)
from backend.jobs.job_manager import job_manager
from fastapi import HTTPException


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(router)


@pytest.fixture
def sample_sequences():
    """Sample sequences for testing."""
    return [
        SequenceInput(
            name="test_antibody_1",
            heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
        ),
        SequenceInput(
            name="test_antibody_2",
            heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
        ),
    ]


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_annotation_endpoint_request_structure(self, client):
        """Test annotation endpoint with proper request structure."""
        # Real request structure
        request_data = {
            "sequences": [
                {
                    "name": "test_antibody",
                    "heavy_chain": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
                }
            ],
            "numbering_scheme": "imgt",
        }

        # Mock the service to avoid full processing
        with patch(
            "backend.services.annotation_service.AnnotationService"
        ) as mock_service:
            mock_result = {
                "sequences": [],
                "numbering_scheme": "imgt",
                "total_sequences": 1,
                "chain_types": {},
                "isotypes": {},
                "species": {},
            }
            mock_service.return_value.process_annotation_request.return_value = (
                Mock()
            )
            mock_service.return_value.process_annotation_request.return_value.model_dump.return_value = (
                mock_result
            )

            response = client.post("/annotate", json=request_data)

            assert response.status_code == 200
            result = response.json()
            assert result["numbering_scheme"] == "imgt"
            assert result["total_sequences"] == 1

    def test_annotation_endpoint_error_handling(self, client):
        """Test annotation endpoint error handling."""
        # Invalid request structure
        invalid_request = {
            "sequences": [],  # Empty sequences
            "numbering_scheme": "invalid_scheme",
        }
        # Test that the client raises a validation error for invalid request
        with pytest.raises(RequestValidationError):
            client.post("/annotate", json=invalid_request)

    def test_msa_upload_endpoint_structure(self, client):
        """Test MSA upload endpoint with file upload."""
        # Mock the service
        with patch("backend.services.msa_service.MSAService") as mock_service:
            mock_service.return_value.process_upload.return_value = ([], [])

            # Test file upload
            response = client.post(
                "/msa-viewer/upload",
                files={
                    "file": (
                        "test.fasta",
                        b">seq1\nEVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEW",
                        "text/plain",
                    )
                },
            )

            assert response.status_code == 200
            result = response.json()
            assert result["success"] is True
            assert "data" in result

    def test_create_msa_job_real(self, client, sample_sequences):
        """Test creating a real MSA job without mocking."""
        # Clean up any existing jobs
        job_manager.cleanup_old_jobs(max_age_hours=0)

        # Create MSA creation request
        request_data = {
            "sequences": [seq.model_dump() for seq in sample_sequences],
            "alignment_method": "muscle",
            "numbering_scheme": "imgt",
        }

        # Create MSA job
        response = client.post("/msa-viewer/create-msa", json=request_data)

        assert response.status_code == 200
        result = response.json()

        # Check response structure
        assert result["success"] is True
        assert "message" in result
        assert "data" in result

        data = result["data"]
        assert "msa_result" in data
        assert "annotation_result" in data
        assert "pssm_data" in data
        assert "consensus" in data
        assert "use_background" in data

        # Check MSA result structure
        msa_result = data["msa_result"]
        assert "msa_id" in msa_result
        assert "sequences" in msa_result
        assert "alignment_matrix" in msa_result
        assert "consensus" in msa_result
        assert "alignment_method" in msa_result
        assert msa_result["alignment_method"] == "muscle"
        assert "metadata" in msa_result
        assert msa_result["metadata"]["num_sequences"] == 2

    def test_job_status_real(self, client, sample_sequences):
        """Test job status endpoint with real job manager."""
        # Clean up any existing jobs
        job_manager.cleanup_old_jobs(max_age_hours=0)

        # Create a real MSA job first
        request_data = {
            "sequences": [seq.model_dump() for seq in sample_sequences],
            "alignment_method": "muscle",
            "numbering_scheme": "imgt",
        }

        response = client.post("/msa-viewer/create-msa", json=request_data)
        assert response.status_code == 200

        # Get the job ID from the response
        msa_result = response.json()
        msa_id = msa_result["data"]["msa_result"]["msa_id"]

        # Create an annotation job using the MSA ID
        annotation_request = {"msa_id": msa_id, "numbering_scheme": "imgt"}

        response = client.post(
            "/msa-viewer/annotate-msa", json=annotation_request
        )
        assert response.status_code == 200

        job_result = response.json()
        job_id = job_result["data"]["job_id"]

        # Wait a bit for the job to start processing
        time.sleep(0.5)

        # Check job status
        response = client.get(f"/msa-viewer/job/{job_id}")
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True
        assert "data" in result

        job_status = result["data"]
        assert "job_id" in job_status
        assert "status" in job_status
        assert "progress" in job_status
        assert "message" in job_status
        assert "created_at" in job_status
        assert job_status["job_id"] == job_id

        # Status should be one of the expected values
        assert job_status["status"] in [
            "pending",
            "running",
            "completed",
            "failed",
        ]
        assert 0.0 <= job_status["progress"] <= 1.0

    def test_job_status_not_found_real(self, client):
        """Test job status endpoint when job doesn't exist."""
        # Clean up any existing jobs
        job_manager.cleanup_old_jobs(max_age_hours=0)

        # Try to get status of non-existent job
        # Since we're using TestClient(router), exceptions are raised directly
        # instead of being converted to HTTP responses
        with pytest.raises(HTTPException) as exc_info:
            client.get("/msa-viewer/job/nonexistent_job_id")

        assert exc_info.value.status_code == 404
        assert "Job not found" in str(exc_info.value.detail)

    def test_list_jobs_real(self, client, sample_sequences):
        """Test list jobs endpoint with real job manager."""
        # Clean up any existing jobs
        job_manager.cleanup_old_jobs(max_age_hours=0)

        # Create a few real jobs
        request_data = {
            "sequences": [seq.model_dump() for seq in sample_sequences],
            "alignment_method": "muscle",
            "numbering_scheme": "imgt",
        }

        # Create first job
        response = client.post("/msa-viewer/create-msa", json=request_data)
        assert response.status_code == 200

        msa_result = response.json()
        msa_id = msa_result["data"]["msa_result"]["msa_id"]

        # Create annotation job
        annotation_request = {"msa_id": msa_id, "numbering_scheme": "imgt"}

        response = client.post(
            "/msa-viewer/annotate-msa", json=annotation_request
        )
        assert response.status_code == 200

        # Wait a bit for jobs to be created
        time.sleep(0.5)

        # List all jobs
        response = client.get("/msa-viewer/jobs")
        assert response.status_code == 200

        result = response.json()
        assert result["success"] is True
        assert "data" in result
        assert "jobs" in result["data"]

        jobs = result["data"]["jobs"]
        assert isinstance(jobs, list)

        # Should have at least one job (the annotation job we just created)
        assert len(jobs) >= 1

        # Check job structure
        for job in jobs:
            assert "job_id" in job
            assert "status" in job
            assert "progress" in job
            assert "message" in job
            assert "created_at" in job
            assert job["status"] in [
                "pending",
                "running",
                "completed",
                "failed",
            ]
            assert 0.0 <= job["progress"] <= 1.0

    def test_job_lifecycle_real(self, client, sample_sequences):
        """Test complete job lifecycle from creation to completion."""
        # Clean up any existing jobs
        job_manager.cleanup_old_jobs(max_age_hours=0)

        # Create MSA job
        request_data = {
            "sequences": [seq.model_dump() for seq in sample_sequences],
            "alignment_method": "muscle",
            "numbering_scheme": "imgt",
        }

        response = client.post("/msa-viewer/create-msa", json=request_data)
        assert response.status_code == 200

        msa_result = response.json()
        msa_id = msa_result["data"]["msa_result"]["msa_id"]

        # Create annotation job
        annotation_request = {"msa_id": msa_id, "numbering_scheme": "imgt"}

        response = client.post(
            "/msa-viewer/annotate-msa", json=annotation_request
        )
        assert response.status_code == 200

        job_result = response.json()
        job_id = job_result["data"]["job_id"]

        # Monitor job progress
        max_wait_time = 30  # seconds
        wait_interval = 0.5  # seconds
        waited_time = 0

        while waited_time < max_wait_time:
            response = client.get(f"/msa-viewer/job/{job_id}")
            assert response.status_code == 200

            result = response.json()
            job_status = result["data"]

            # Check if job completed
            if job_status["status"] in ["completed", "failed"]:
                break

            time.sleep(wait_interval)
            waited_time += wait_interval

        # Final status check
        response = client.get(f"/msa-viewer/job/{job_id}")
        assert response.status_code == 200

        result = response.json()
        job_status = result["data"]

        # Job should be in a terminal state
        assert job_status["status"] in ["completed", "failed"]
        assert (
            job_status["progress"] == 1.0
            if job_status["status"] == "completed"
            else True
        )
        assert "completed_at" in job_status

        # If completed, should have result
        if job_status["status"] == "completed":
            assert "result" in job_status
            assert job_status["result"] is not None
