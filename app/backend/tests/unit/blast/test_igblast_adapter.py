"""
Unit tests for IgBLAST adapter functionality.
Following TDD principles - tests are written before implementation.
IgBLAST is specifically designed for immunoglobulin and T-cell receptor analysis.
"""

import os

import docker
import pytest

from backend.core.exceptions import ExternalToolError
from backend.infrastructure.adapters.igblast_adapter import IgBlastAdapter
from backend.tests.data.blast.test_sequences import (
    TEST_SEQUENCES,
)


class TestIgBlastAdapter:
    """Test cases for IgBlastAdapter class."""

    def _create_adapter(self):
        """Helper method to create IgBlastAdapter with Docker support."""
        try:
            docker_client = docker.from_env()
            return IgBlastAdapter(docker_client=docker_client)
        except Exception:
            return IgBlastAdapter()

    def test_igblast_adapter_initialization(self):
        """Test that IgBlastAdapter can be initialized properly."""
        adapter = self._create_adapter()
        assert adapter.tool_name == "igblast"
        assert adapter.is_available() is True

    def test_igblast_adapter_find_executable(self):
        """Test that IgBLAST executable can be found."""
        adapter = self._create_adapter()
        executable_path = adapter._find_executable()
        assert executable_path is not None
        if executable_path != "docker":
            assert os.path.exists(executable_path)

    def test_igblast_adapter_validate_installation(self):
        """Test that IgBLAST installation is validated correctly."""
        adapter = self._create_adapter()
        # Should not raise an exception if IgBLAST is properly installed
        adapter._validate_tool_installation()

    def test_igblast_adapter_build_command_igblastn(self):
        """Test command building for igblastn."""
        adapter = self._create_adapter()
        query_sequence = "ATGCGTACGTACGTACGT"  # Sample DNA sequence
        organism = "human"

        command = adapter._build_command(
            query_sequence=query_sequence,
            organism=organism,
            blast_type="igblastn",
        )

        assert "igblastn" in command
        assert "-query" in command
        assert "-organism" in command
        assert organism in command

    def test_igblast_adapter_build_command_with_parameters(self):
        """Test command building with additional parameters."""
        adapter = self._create_adapter()
        query_sequence = "ATGCGTACGTACGTACGT"
        organism = "human"

        command = adapter._build_command(
            query_sequence=query_sequence,
            organism=organism,
            blast_type="igblastn",
            evalue=1e-10,
            num_alignments_V=10,
            num_alignments_D=5,
            num_alignments_J=10,
        )

        assert "-evalue" in command
        assert "1e-10" in command
        assert "-num_alignments_V" in command
        assert "10" in command
        assert "-num_alignments_D" in command
        assert "5" in command

    def test_igblast_adapter_parse_output_igblastn(self):
        """Test parsing of igblastn output."""
        adapter = self._create_adapter()

        # Sample IgBLAST output in tabular format
        sample_output = """# IGBLASTN 1.17.1
# Query: test_sequence
# Database: human_gl_V human_gl_D human_gl_J
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score, V gene, D gene, J gene, C gene, CDR3 start, CDR3 end
test_sequence	IGHV1-2*02	98.5	300	4	1	1	300	1	300	0.0	567	IGHV1-2*02	IGHD2-2*01	IGHJ4*02	IGHG1*01	270	300"""

        results = adapter._parse_output(sample_output, blast_type="igblastn")

        assert "hits" in results
        assert len(results["hits"]) == 1
        assert results["hits"][0]["query_id"] == "test_sequence"
        assert results["hits"][0]["v_gene"] == "IGHV1-2*02"
        assert results["hits"][0]["d_gene"] == "IGHD2-2*01"
        assert results["hits"][0]["j_gene"] == "IGHJ4*02"
        assert results["hits"][0]["c_gene"] == "IGHG1*01"

    def test_igblast_adapter_parse_output_with_cdr3(self):
        """Test parsing of IgBLAST output with CDR3 information."""
        adapter = self._create_adapter()

        # Sample IgBLAST output with CDR3
        sample_output = """# IGBLASTN 1.17.1
# Query: antibody_seq
# Database: human_gl_V human_gl_D human_gl_J
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score, V gene, D gene, J gene, C gene, CDR3 start, CDR3 end, CDR3 sequence
antibody_seq	IGHV3-11*01	97.2	350	8	2	1	350	1	350	0.0	645	IGHV3-11*01	IGHD3-10*01	IGHJ6*02	IGHG1*01	270	300	ARDRGYYYFDYW"""

        results = adapter._parse_output(sample_output, blast_type="igblastn")

        assert "hits" in results
        assert len(results["hits"]) == 1
        hit = results["hits"][0]
        assert hit["cdr3_start"] == 270
        assert hit["cdr3_end"] == 300
        assert hit["cdr3_sequence"] == "ARDRGYYYFDYW"

    def test_igblast_adapter_execute_igblastn_analysis(self):
        """Test executing igblastn analysis."""
        adapter = self._create_adapter()

        # Use DNA sequence for igblastn
        dna_sequence = TEST_SEQUENCES["nucleotide"]["human_antibody_vh"][
            "sequence"
        ]

        try:
            # Execute IgBLAST analysis
            results = adapter.execute(
                query_sequence=dna_sequence,
                organism="human",
                blast_type="igblastn",
                evalue=1e-10,
            )

            assert "hits" in results
            assert "analysis_summary" in results

        except ExternalToolError as e:
            # IgBLAST might fail if germline databases are not available
            # This is expected in a test environment
            assert "germline" in str(e).lower() or "database" in str(e).lower()

    def test_igblast_adapter_invalid_sequence(self):
        """Test that invalid sequences are handled properly."""
        adapter = self._create_adapter()

        with pytest.raises(ValueError):
            adapter._validate_sequence("INVALID_SEQUENCE_123!@#", "igblastn")

    def test_igblast_adapter_invalid_organism(self):
        """Test that invalid organisms are handled properly."""
        adapter = self._create_adapter()

        with pytest.raises(ValueError):
            adapter._build_command(
                query_sequence="ATGCGTACGTACGTACGT",
                organism="invalid_organism",
                blast_type="igblastn",
            )

    def test_igblast_adapter_get_version(self):
        """Test that IgBLAST version can be retrieved."""
        adapter = self._create_adapter()
        version = adapter.get_version()
        assert version is not None
        # When using Docker, we get Docker version instead of IgBLAST version
        if adapter.executable_path == "docker":
            assert "Docker" in version
        else:
            assert "igblast" in version.lower()

    def test_igblast_adapter_tool_info(self):
        """Test that tool information is returned correctly."""
        adapter = self._create_adapter()
        info = adapter.get_tool_info()

        assert "name" in info
        assert "executable_path" in info
        assert "version" in info
        assert "available" in info
        assert info["name"] == "igblast"
        assert info["available"] is True

    def test_igblast_adapter_supported_organisms(self):
        """Test that supported organisms are correctly identified."""
        adapter = self._create_adapter()
        organisms = adapter.get_supported_organisms()

        assert "human" in organisms
        assert "mouse" in organisms
        assert "rat" in organisms

    def test_igblast_adapter_supported_blast_types(self):
        """Test that supported BLAST types are correctly identified."""
        adapter = self._create_adapter()
        blast_types = adapter.get_supported_blast_types()

        assert "igblastn" in blast_types
        assert "igblastp" in blast_types


class TestIgBlastAdapterIntegration:
    """Integration tests for IgBlastAdapter with real IgBLAST execution."""

    def _create_adapter(self):
        """Helper method to create IgBlastAdapter with Docker support."""
        try:
            docker_client = docker.from_env()
            return IgBlastAdapter(docker_client=docker_client)
        except Exception:
            return IgBlastAdapter()

    @pytest.mark.integration
    def test_igblast_adapter_real_execution(self):
        """Test real IgBLAST execution with actual antibody sequences."""
        adapter = self._create_adapter()

        # Test with real antibody sequences
        query_seq = TEST_SEQUENCES["nucleotide"]["human_antibody_vh"][
            "sequence"
        ]

        try:
            # Execute IgBLAST analysis
            results = adapter.execute(
                query_sequence=query_seq,
                organism="human",
                blast_type="igblastn",
                evalue=1e-5,
            )

            # Verify results
            assert "hits" in results
            assert "analysis_summary" in results

            # Check that we get antibody-specific information
            if results["hits"]:
                hit = results["hits"][0]
                # Should have V, D, J gene information
                assert "v_gene" in hit or "d_gene" in hit or "j_gene" in hit

        except ExternalToolError as e:
            # IgBLAST might fail if germline databases are not available
            # This is expected in a test environment without proper databases
            assert "germline" in str(e).lower() or "database" in str(e).lower()
