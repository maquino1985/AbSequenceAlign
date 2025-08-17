"""
Unit tests for BLAST adapter functionality.
Following TDD principles - tests are written before implementation.
"""

import pytest
import tempfile
import os
import docker

from backend.infrastructure.adapters.blast_adapter import BlastAdapter
from backend.core.exceptions import ExternalToolError
from backend.tests.data.blast.test_sequences import (
    HUMAN_IGG1_CONSTANT,
    HUMAN_IGG2_CONSTANT,
    TEST_SEQUENCES,
)


class TestBlastAdapter:
    """Test cases for BlastAdapter class."""

    def _create_adapter(self):
        """Helper method to create BlastAdapter with Docker support."""
        try:
            docker_client = docker.from_env()
            return BlastAdapter(docker_client=docker_client)
        except Exception:
            return BlastAdapter()

    def test_blast_adapter_initialization(self):
        """Test that BlastAdapter can be initialized properly."""
        adapter = self._create_adapter()
        assert adapter.tool_name == "blast"
        assert adapter.is_available() is True

    def test_blast_adapter_find_executable(self):
        """Test that BLAST executable can be found."""
        adapter = self._create_adapter()
        executable_path = adapter._find_executable()
        assert executable_path is not None
        if executable_path != "docker":
            assert os.path.exists(executable_path)

    def test_blast_adapter_validate_installation(self):
        """Test that BLAST installation is validated correctly."""
        adapter = self._create_adapter()
        # Should not raise an exception if BLAST is properly installed
        adapter._validate_tool_installation()

    def test_blast_adapter_build_command_blastp(self):
        """Test command building for blastp."""
        adapter = self._create_adapter()
        query_sequence = HUMAN_IGG1_CONSTANT["sequence"]
        database = "test_db"

        command = adapter._build_command(
            query_sequence=query_sequence,
            database=database,
            blast_type="blastp",
        )

        assert "blastp" in command
        assert "-query" in command
        assert "-db" in command
        assert database in command

    def test_blast_adapter_build_command_blastn(self):
        """Test command building for blastn."""
        adapter = self._create_adapter()
        query_sequence = "ATGCGTACGTACGTACGT"  # Sample DNA sequence
        database = "test_db"

        command = adapter._build_command(
            query_sequence=query_sequence,
            database=database,
            blast_type="blastn",
        )

        assert "blastn" in command
        assert "-query" in command
        assert "-db" in command
        assert database in command

    def test_blast_adapter_build_command_with_parameters(self):
        """Test command building with additional parameters."""
        adapter = self._create_adapter()
        query_sequence = HUMAN_IGG1_CONSTANT["sequence"]
        database = "test_db"

        command = adapter._build_command(
            query_sequence=query_sequence,
            database=database,
            blast_type="blastp",
            evalue=1e-10,
            max_target_seqs=10,
            outfmt="6",
        )

        assert "-evalue" in command
        assert "1e-10" in command
        assert "-max_target_seqs" in command
        assert "10" in command
        assert "-outfmt" in command
        assert "6" in command

    def test_blast_adapter_parse_output_blastp(self):
        """Test parsing of blastp output."""
        adapter = self._create_adapter()

        # Sample BLAST output in tabular format (outfmt 6)
        sample_output = """P01857.2	P01859.3	99.2	330	2	1	1	330	1	330	0.0	667
P01857.2	P01860.3	98.8	330	3	1	1	330	1	330	0.0	665
P01857.2	P01861.3	98.5	330	4	1	1	330	1	330	0.0	663"""

        results = adapter._parse_output(
            sample_output, blast_type="blastp", outfmt="6"
        )

        assert "hits" in results
        assert len(results["hits"]) == 3
        assert results["hits"][0]["query_id"] == "P01857.2"
        assert results["hits"][0]["subject_id"] == "P01859.3"
        assert results["hits"][0]["identity"] == 99.2
        assert results["hits"][0]["evalue"] == 0.0

    def test_blast_adapter_parse_output_with_headers(self):
        """Test parsing of BLAST output with headers."""
        adapter = self._create_adapter()

        # Sample BLAST output with headers
        sample_output = """# BLASTP 2.13.0+
# Query: P01857.2
# Database: test_db
# Fields: query acc.ver, subject acc.ver, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
P01857.2	P01859.3	99.2	330	2	1	1	330	1	330	0.0	667"""

        results = adapter._parse_output(
            sample_output, blast_type="blastp", outfmt="6"
        )

        assert "hits" in results
        assert len(results["hits"]) == 1
        assert results["query_info"]["query_id"] == "P01857.2"

    def test_blast_adapter_execute_blastp_against_test_database(self):
        """Test executing blastp against a test database."""
        adapter = self._create_adapter()

        # Create a temporary FASTA file with test sequences
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as f:
            f.write(
                f">{HUMAN_IGG1_CONSTANT['name']}\n{HUMAN_IGG1_CONSTANT['sequence']}\n"
            )
            f.write(
                f">{HUMAN_IGG2_CONSTANT['name']}\n{HUMAN_IGG2_CONSTANT['sequence']}\n"
            )
            temp_fasta = f.name

        try:
            # Create BLAST database
            adapter._create_blast_database(temp_fasta, "test_db")

            # Execute BLAST search
            results = adapter.execute(
                query_sequence=HUMAN_IGG1_CONSTANT["sequence"],
                database="test_db",
                blast_type="blastp",
                evalue=1e-10,
                max_target_seqs=5,
            )

            assert "hits" in results
            assert len(results["hits"]) > 0

            # Should find itself and IgG2 (high similarity)
            hit_ids = [hit["subject_id"] for hit in results["hits"]]
            assert any("IGHG1" in hit_id for hit_id in hit_ids)
            assert any("IGHG2" in hit_id for hit_id in hit_ids)

        finally:
            # Cleanup
            os.unlink(temp_fasta)
            adapter._cleanup_blast_database("test_db")

    def test_blast_adapter_invalid_sequence(self):
        """Test that invalid sequences are handled properly."""
        adapter = self._create_adapter()

        with pytest.raises(ValueError):
            adapter._validate_sequence("INVALID_SEQUENCE_123!@#", "blastp")

    def test_blast_adapter_invalid_database(self):
        """Test that invalid database paths are handled properly."""
        adapter = self._create_adapter()

        with pytest.raises(ExternalToolError):
            adapter.execute(
                query_sequence=HUMAN_IGG1_CONSTANT["sequence"],
                database="nonexistent_database",
                blast_type="blastp",
            )

    def test_blast_adapter_timeout_handling(self):
        """Test that timeouts are handled properly."""
        adapter = self._create_adapter()

        # This test would require a very large database to trigger timeout
        # For now, we'll test the timeout configuration
        adapter._get_timeout() == 300  # 5 minutes default

    def test_blast_adapter_get_version(self):
        """Test that BLAST version can be retrieved."""
        adapter = self._create_adapter()
        version = adapter.get_version()
        assert version is not None
        # When using Docker, we get Docker version instead of BLAST version
        if adapter.executable_path == "docker":
            assert "Docker" in version
        else:
            assert "blast" in version.lower()

    def test_blast_adapter_tool_info(self):
        """Test that tool information is returned correctly."""
        adapter = self._create_adapter()
        info = adapter.get_tool_info()

        assert "name" in info
        assert "executable_path" in info
        assert "version" in info
        assert "available" in info
        assert info["name"] == "blast"
        assert info["available"] is True


class TestBlastAdapterIntegration:
    """Integration tests for BlastAdapter with real BLAST execution."""

    def _create_adapter(self):
        """Helper method to create BlastAdapter with Docker support."""
        try:
            docker_client = docker.from_env()
            return BlastAdapter(docker_client=docker_client)
        except Exception:
            return BlastAdapter()

    @pytest.mark.integration
    def test_blast_adapter_real_execution(self):
        """Test real BLAST execution with actual sequences."""
        adapter = self._create_adapter()

        # Test with real antibody sequences
        query_seq = HUMAN_IGG1_CONSTANT["sequence"]

        # Create a small test database
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as f:
            for seq_name, seq_data in TEST_SEQUENCES["protein"].items():
                f.write(f">{seq_data['name']}\n{seq_data['sequence']}\n")
            temp_fasta = f.name

        try:
            # Create database
            adapter._create_blast_database(temp_fasta, "integration_test_db")

            # Execute search
            results = adapter.execute(
                query_sequence=query_seq,
                database="integration_test_db",
                blast_type="blastp",
                evalue=1e-5,
                max_target_seqs=10,
            )

            # Verify results
            assert "hits" in results
            assert len(results["hits"]) > 0

            # Check that we get hits for similar sequences
            hit_ids = [hit.get("subject_id", "") for hit in results["hits"]]

            # Check for IGHG in either subject_id or subject_def
            has_ighg = any(
                "IGHG" in hit.get("subject_id", "")
                or "IGHG" in hit.get("subject_def", "")
                for hit in results["hits"]
            )
            assert has_ighg, f"No IGHG sequences found in hits: {hit_ids}"

        finally:
            # Cleanup
            os.unlink(temp_fasta)
            adapter._cleanup_blast_database("integration_test_db")
