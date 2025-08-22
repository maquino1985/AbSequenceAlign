"""
Integration tests for API endpoints with real request/response handling.
"""

import time
from unittest.mock import patch, Mock

import pytest
from fastapi.testclient import TestClient

from backend.api.v2.blast_endpoints import router as blast_router
from backend.api.v2.endpoints import router
from backend.jobs.job_manager import job_manager
from backend.models.models import (
    SequenceInput,
)


@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    app.include_router(blast_router, prefix="/blast")
    return TestClient(app)


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
        # Test that the client returns a validation error response for invalid request
        response = client.post("/annotate", json=invalid_request)
        assert response.status_code == 422  # Validation error status code
        result = response.json()
        assert "detail" in result  # Should have validation error details

    @pytest.mark.skip(
        reason="Real service test - skip for now to focus on unit tests"
    )
    def test_blast_databases_endpoint_real(self, client):
        """Test BLAST databases endpoint with real service."""
        response = client.get("/blast/databases")

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "databases" in result["data"]
        assert "public" in result["data"]["databases"]
        # Check that we have at least one database
        assert len(result["data"]["databases"]["public"]) > 0

    @pytest.mark.skip(
        reason="Real service test - skip for now to focus on unit tests"
    )
    def test_blast_organisms_endpoint_real(self, client):
        """Test BLAST organisms endpoint with real service."""
        response = client.get("/blast/organisms")

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "organisms" in result["data"]
        # Check that we have at least one organism
        assert len(result["data"]["organisms"]) > 0
        # Should include human and mouse
        organisms = result["data"]["organisms"]
        assert "human" in organisms or "mouse" in organisms

    def test_blast_search_public_endpoint_real(self, client):
        """Test BLAST public search endpoint with real service."""
        # Use the verified working protein sequence
        request_data = {
            "query_sequence": "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS",
            "databases": ["swissprot"],
            "blast_type": "blastp",
            "evalue": 1e-10,
            "max_target_seqs": 5,
        }

        response = client.post("/blast/search/public", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "results" in result["data"]
        assert result["data"]["results"]["blast_type"] == "blastp"
        # Should have some hits for this known antibody sequence
        assert len(result["data"]["results"]["hits"]) > 0

        # Check hit structure
        hit = result["data"]["results"]["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert (
            "identity" in hit
        )  # Public BLAST uses "identity", IgBLAST uses "percent_identity"
        assert "evalue" in hit
        assert "bit_score" in hit

    def test_blast_search_antibody_endpoint_nucleotide_real(self, client):
        """Test BLAST antibody search endpoint with real service - nucleotide."""
        request_data = {
            "query_sequence": "CAGGTGCAGCTGGTGGAGTCTGGGGGAGGCGTGGTCCAGCCTGGGAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTAGCAGCTATGCCATGAGCTGGGTCCGCCAGGCTCCAGGCAAGGGGCTGGAGTGGGTGGCAGTTATATCATATGATGGAAGTAATAAATACTATGCAGACTCCGTGAAGGGCCGATTCACCATCTCCAGAGACAATTCCAAGAACACGCTGTATCTGCAAATGAACAGCCTGAGAGCCGAGGACACGGCTGTGTATTACTGTGCGAGAGA",
            "organism": "human",
            "blast_type": "igblastn",
            "evalue": 1e-10,
        }

        response = client.post("/blast/search/antibody", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "results" in result["data"]
        assert result["data"]["results"]["blast_type"] == "igblastn"
        # Should have some hits for this known nucleotide sequence
        assert len(result["data"]["results"]["hits"]) > 0

        # Check hit structure for nucleotide search
        hit = result["data"]["results"]["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert (
            "percent_identity" in hit
        )  # Changed from "identity" to "percent_identity"
        assert "v_gene" in hit
        assert hit["v_gene"] is not None  # Should have V gene assignment
        assert (
            "IGHV3-30" in hit["v_gene"]
        )  # Should match expected V gene family
        assert (
            hit["percent_identity"] > 95.0
        )  # Changed from "identity" to "percent_identity"

    def test_blast_search_antibody_endpoint_protein_real(self, client):
        """Test BLAST antibody search endpoint with real service - protein."""
        request_data = {
            "query_sequence": "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS",
            "organism": "human",
            "blast_type": "igblastp",
            "evalue": 1e-10,
        }

        response = client.post("/blast/search/antibody", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "results" in result["data"]
        assert result["data"]["results"]["blast_type"] == "igblastp"
        # Should have some hits for this known protein sequence
        assert len(result["data"]["results"]["hits"]) > 0

        # Check hit structure for protein search
        hit = result["data"]["results"]["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert (
            "percent_identity" in hit
        )  # Changed from "identity" to "percent_identity"
        assert "v_gene" in hit
        assert hit["v_gene"] is not None  # Should have V gene assignment
        assert (
            "IGHV3-9" in hit["v_gene"]
        )  # Should match expected V gene family
        assert (
            hit["percent_identity"] > 90.0
        )  # Changed from "identity" to "percent_identity"

        # For protein searches, D/J/C genes should be None or not present
        # Check if fields exist, and if they do, they should be None
        if "d_gene" in hit:
            assert hit["d_gene"] is None
        if "j_gene" in hit:
            assert hit["j_gene"] is None
        if "c_gene" in hit:
            assert hit["c_gene"] is None

    def test_blast_search_antibody_endpoint_protein_with_domain_system(
        self, client
    ):
        """Test BLAST antibody search endpoint with domain system parameter."""
        request_data = {
            "query_sequence": "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS",
            "organism": "human",
            "blast_type": "igblastp",
            "evalue": 1e-10,
            "domain_system": "imgt",
        }

        response = client.post("/blast/search/antibody", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "results" in result["data"]
        assert result["data"]["results"]["blast_type"] == "igblastp"

        # Check that framework/CDR data is present in analysis summary
        analysis_summary = result["data"]["results"]["analysis_summary"]
        framework_cdr_fields = [
            k
            for k in analysis_summary.keys()
            if any(
                region in k for region in ["fr1", "cdr1", "fr2", "cdr2", "fr3"]
            )
        ]
        assert (
            len(framework_cdr_fields) > 0
        ), "Framework/CDR data should be present"

    def test_blast_search_antibody_endpoint_protein_with_kabat_domain_system(
        self, client
    ):
        """Test BLAST antibody search endpoint with Kabat domain system."""
        request_data = {
            "query_sequence": "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS",
            "organism": "human",
            "blast_type": "igblastp",
            "evalue": 1e-10,
            "domain_system": "kabat",
        }

        response = client.post("/blast/search/antibody", json=request_data)

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "results" in result["data"]

        # Check that framework/CDR data is present with Kabat numbering
        analysis_summary = result["data"]["results"]["analysis_summary"]
        framework_cdr_fields = [
            k
            for k in analysis_summary.keys()
            if any(
                region in k for region in ["fr1", "cdr1", "fr2", "cdr2", "fr3"]
            )
        ]
        assert (
            len(framework_cdr_fields) > 0
        ), "Framework/CDR data should be present with Kabat numbering"

    def test_blast_search_antibody_endpoint_invalid_domain_system(
        self, client
    ):
        """Test BLAST antibody search endpoint with invalid domain system."""
        request_data = {
            "query_sequence": "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS",
            "organism": "human",
            "blast_type": "igblastp",
            "evalue": 1e-10,
            "domain_system": "invalid_system",
        }

        response = client.post("/blast/search/antibody", json=request_data)

        # Should return an error for invalid domain system
        assert response.status_code == 400
        result = response.json()
        assert "Unsupported domain system" in result["detail"]

    def test_blast_search_antibody_endpoint_domain_system_nucleotide_ignored(
        self, client
    ):
        """Test that domain system parameter is ignored for nucleotide IgBLAST."""
        request_data = {
            "query_sequence": "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAGTGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGCGCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGTGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGCATCAGGATTGGCTGAACGGCAAAGAATATAAATGCAAAGTGAGCAACAAAGCGCTGCCGGCGCCGATTGAAAAAACCATTAGCAAAGCGAAGGCCAGCCGCGCGAACCGCAGGTGTATACCCTGCCGCCGAGCCGCGATGAACTGACCAAAAACCAGGTGAGCCTGACCTGCCTGGTGAAAGGCTTTTATCCGAGCGATATTGCGGTGGAATGGGAAAGCAACGGCCAGCCGGAAAACAACTATAAAACCACCCCGCCGGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA",
            "organism": "human",
            "blast_type": "igblastn",
            "evalue": 1e-10,
            "domain_system": "imgt",  # Should be ignored for nucleotide
        }

        response = client.post("/blast/search/antibody", json=request_data)

        # Should work normally (domain system ignored for nucleotide)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "results" in result["data"]
        assert result["data"]["results"]["blast_type"] == "igblastn"

    def test_blast_endpoints_error_handling_real(self, client):
        """Test BLAST endpoints error handling with real services."""
        # Test with invalid sequence
        request_data = {
            "query_sequence": "INVALID_SEQUENCE_123!@#",
            "databases": ["swissprot"],
            "blast_type": "blastp",
            "evalue": 1e-10,
            "max_target_seqs": 5,
        }

        response = client.post("/blast/search/public", json=request_data)

        # Should handle invalid sequences gracefully
        assert response.status_code in [
            400,
            500,
        ]  # Either validation error or execution error

        # Test with invalid organism
        request_data = {
            "query_sequence": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK",
            "organism": "invalid_organism",
            "blast_type": "igblastp",
            "evalue": 1e-10,
        }

        response = client.post("/blast/search/antibody", json=request_data)

        # Should handle invalid organisms gracefully
        assert response.status_code in [400, 500]

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
        # TestClient converts exceptions to HTTP responses
        response = client.get("/msa-viewer/job/nonexistent_job_id")
        assert response.status_code == 404
        result = response.json()
        assert "Job not found" in result["detail"]

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
