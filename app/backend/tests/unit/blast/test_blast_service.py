"""
Unit tests for BLAST service functionality.
Following TDD principles - tests are written before implementation.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from backend.services.blast_service import BlastService
from backend.services.igblast_service import IgBlastService
from backend.tests.data.blast.test_sequences import (
    HUMAN_IGG1_CONSTANT,
    TEST_SEQUENCES,
)


class TestBlastService:
    """Test cases for BlastService class."""

    def test_blast_service_initialization(self):
        """Test that BlastService can be initialized properly."""
        service = BlastService()
        assert service is not None
        assert hasattr(service, "blast_adapter")
        assert hasattr(service, "igblast_adapter")

    def test_blast_service_search_public_databases(self):
        """Test searching against public databases."""
        # Create mock adapters
        mock_blast_adapter = Mock()
        mock_igblast_adapter = Mock()
        mock_job_repository = Mock()

        service = BlastService(
            blast_adapter=mock_blast_adapter,
            igblast_adapter=mock_igblast_adapter,
            job_repository=mock_job_repository,
        )

        # Mock the blast adapter
        mock_results = {
            "hits": [
                {
                    "query_id": "query",
                    "subject_id": "P01857.2",
                    "identity": 99.5,
                    "evalue": 0.0,
                    "bit_score": 800.0,
                }
            ],
            "total_hits": 1,
        }

        mock_blast_adapter.execute.return_value = mock_results

        results = service.search_public_databases(
            query_sequence=HUMAN_IGG1_CONSTANT["sequence"],
            databases=["nr"],
            blast_type="blastp",
            evalue=1e-10,
        )

        assert results is not None
        assert "hits" in results
        assert len(results["hits"]) == 1

    def test_blast_service_search_internal_database(self):
        """Test searching against internal database."""
        # Create mock adapters
        mock_blast_adapter = Mock()
        mock_igblast_adapter = Mock()
        mock_job_repository = Mock()

        service = BlastService(
            blast_adapter=mock_blast_adapter,
            igblast_adapter=mock_igblast_adapter,
            job_repository=mock_job_repository,
        )

        # Mock the blast adapter
        mock_results = {
            "hits": [
                {
                    "query_id": "query",
                    "subject_id": "internal_seq_1",
                    "identity": 95.0,
                    "evalue": 1e-50,
                    "bit_score": 600.0,
                }
            ],
            "total_hits": 1,
        }

        mock_blast_adapter.execute.return_value = mock_results

        results = service.search_internal_database(
            query_sequence=HUMAN_IGG1_CONSTANT["sequence"],
            blast_type="blastp",
            evalue=1e-10,
        )

        assert results is not None
        assert "hits" in results
        assert len(results["hits"]) == 1

    def test_blast_service_create_custom_database(self):
        """Test creating custom BLAST database."""
        # Create mock adapters
        mock_blast_adapter = Mock()
        mock_igblast_adapter = Mock()
        mock_job_repository = Mock()

        service = BlastService(
            blast_adapter=mock_blast_adapter,
            igblast_adapter=mock_igblast_adapter,
            job_repository=mock_job_repository,
        )

        sequences = [
            {
                "name": "test_seq_1",
                "sequence": HUMAN_IGG1_CONSTANT["sequence"],
                "description": "Test sequence 1",
            }
        ]

        result = service.create_custom_database(
            sequences=sequences, database_name="test_db"
        )

        assert result is not None
        mock_blast_adapter._create_blast_database.assert_called_once()

    def test_blast_service_get_available_databases(self):
        """Test getting available databases."""
        service = BlastService()

        databases = service.get_available_databases()

        assert "public" in databases
        assert "custom" in databases
        assert "internal" in databases

    def test_blast_service_validate_sequence(self):
        """Test sequence validation."""
        service = BlastService()

        # Valid protein sequence
        is_valid = service.validate_sequence(
            sequence=HUMAN_IGG1_CONSTANT["sequence"], sequence_type="protein"
        )
        assert is_valid is True

        # Invalid sequence
        is_valid = service.validate_sequence(
            sequence="INVALID_SEQUENCE_123!@#", sequence_type="protein"
        )
        assert is_valid is False

    def test_blast_service_get_job_status(self):
        """Test getting job status."""
        service = BlastService()

        # Mock job repository
        mock_job = {
            "id": "test_job_123",
            "status": "completed",
            "results": {"hits": []},
        }

        with patch.object(
            service.job_repository, "get_job", return_value=mock_job
        ):
            status = service.get_job_status("test_job_123")

            assert status is not None
            assert status["status"] == "completed"


class TestIgBlastService:
    """Test cases for IgBlastService class."""

    def test_igblast_service_initialization(self):
        """Test that IgBlastService can be initialized properly."""
        service = IgBlastService()
        assert service is not None
        assert hasattr(service, "igblast_adapter")

    def test_igblast_service_analyze_antibody_sequence(self):
        """Test antibody sequence analysis."""
        # Create mock adapter
        mock_igblast_adapter = Mock()

        service = IgBlastService(igblast_adapter=mock_igblast_adapter)

        # Mock the igblast adapter
        mock_results = {
            "hits": [
                {
                    "query_id": "query",
                    "v_gene": "IGHV1-2*02",
                    "d_gene": "IGHD2-2*01",
                    "j_gene": "IGHJ4*02",
                    "c_gene": "IGHG1*01",
                    "cdr3_sequence": "ARDRGYYYFDYW",
                    "identity": 98.5,
                }
            ],
            "analysis_summary": {
                "best_v_gene": "IGHV1-2*02",
                "best_d_gene": "IGHD2-2*01",
                "best_j_gene": "IGHJ4*02",
                "best_c_gene": "IGHG1*01",
                "cdr3_sequence": "ARDRGYYYFDYW",
            },
        }

        dna_sequence = TEST_SEQUENCES["nucleotide"]["human_antibody_vh"][
            "sequence"
        ]

        mock_igblast_adapter.execute.return_value = mock_results

        results = service.analyze_antibody_sequence(
            query_sequence=dna_sequence,
            organism="human",
            blast_type="igblastn",
        )

        assert results is not None
        assert "hits" in results
        assert "analysis_summary" in results
        assert results["analysis_summary"]["best_v_gene"] == "IGHV1-2*02"

    def test_igblast_service_get_supported_organisms(self):
        """Test getting supported organisms."""
        # Create mock adapter
        mock_igblast_adapter = Mock()
        mock_igblast_adapter.get_supported_organisms.return_value = [
            "human",
            "mouse",
            "rat",
        ]

        service = IgBlastService(igblast_adapter=mock_igblast_adapter)

        organisms = service.get_supported_organisms()

        assert "human" in organisms
        assert "mouse" in organisms
        assert "rat" in organisms

    def test_igblast_service_validate_antibody_sequence(self):
        """Test antibody sequence validation."""
        service = IgBlastService()

        # Valid DNA sequence
        dna_sequence = TEST_SEQUENCES["nucleotide"]["human_antibody_vh"][
            "sequence"
        ]
        is_valid = service.validate_antibody_sequence(
            sequence=dna_sequence, sequence_type="nucleotide"
        )
        assert is_valid is True

        # Invalid sequence
        is_valid = service.validate_antibody_sequence(
            sequence="INVALID_SEQUENCE_123!@#", sequence_type="nucleotide"
        )
        assert is_valid is False

    def test_igblast_service_extract_cdr3(self):
        """Test CDR3 extraction from results."""
        service = IgBlastService()

        mock_results = {
            "hits": [
                {
                    "cdr3_sequence": "ARDRGYYYFDYW",
                    "cdr3_start": 270,
                    "cdr3_end": 300,
                }
            ]
        }

        cdr3_info = service.extract_cdr3(mock_results)

        assert cdr3_info is not None
        assert cdr3_info["sequence"] == "ARDRGYYYFDYW"
        assert cdr3_info["start"] == 270
        assert cdr3_info["end"] == 300

    def test_igblast_service_get_gene_assignments(self):
        """Test gene assignment extraction."""
        service = IgBlastService()

        mock_results = {
            "hits": [
                {
                    "v_gene": "IGHV1-2*02",
                    "d_gene": "IGHD2-2*01",
                    "j_gene": "IGHJ4*02",
                    "c_gene": "IGHG1*01",
                }
            ]
        }

        gene_assignments = service.get_gene_assignments(mock_results)

        assert gene_assignments is not None
        assert gene_assignments["v_gene"] == "IGHV1-2*02"
        assert gene_assignments["d_gene"] == "IGHD2-2*01"
        assert gene_assignments["j_gene"] == "IGHJ4*02"
        assert gene_assignments["c_gene"] == "IGHG1*01"
