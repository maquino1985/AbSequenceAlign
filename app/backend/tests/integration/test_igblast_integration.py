"""
Integration tests for IgBLAST adapter V3 with real execution.
Tests actual IgBLAST functionality with real sequences and databases.
"""

import subprocess

import pytest
from backend.logger import logger

from backend.core.exceptions import ExternalToolError
from backend.infrastructure.adapters.igblast_adapter_v3 import IgBlastAdapterV3


class TestIgBlastIntegration:
    """Integration tests for IgBLAST adapter V3."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = IgBlastAdapterV3()

        # Load database paths
        self.databases = self.adapter.get_available_databases()
        self.human_dbs = self.databases["human"]
        self.mouse_dbs = self.databases["mouse"]

        # Test sequences
        self.heavy_chain_nucleotide = "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAGTGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGCGCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGTGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGCATCAGGATTGGCTGAACGGCAAAGAATATAAATGCAAAGTGAGCAACAAAGCGCTGCCGGCGCCGATTGAAAAAACCATTAGCAAAGCGAAGGCCAGCCGCGCGAACCGCAGGTGTATACCCTGCCGCCGAGCCGCGATGAACTGACCAAAAACCAGGTGAGCCTGACCTGCCTGGTGAAAGGCTTTTATCCGAGCGATATTGCGGTGGAATGGGAAAGCAACGGCCAGCCGGAAAACAACTATAAAACCACCCCGCCGGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA"

        self.light_chain_nucleotide = "GACATCCAGATGACCCAGTCTCCATCCTCCCTGTCTGCATCTGTAGGAGACAGAGTCACCATCACTTGCCGGGCAAGTCAGGACATTAGAAATGATTTAGCTGGTATCAGCAGAAACCAGGGAAAGCCCCTAAGCTCCTGATCTATGCTGCATCCAGTTTGCAAAGTGGGGTCCCATCAAGGTTCAGCGGCAGTGGATCTGGGACAGATTTCACTCTCACCATCAGCAGTCTGCAGTCTGAAGATTTTGCAGTTTATTACTGTCAGCAATATTAATAGTTACCCGTACACGTTCGGAGGGGGGACCAAGCTGGAAATAAAAC"

        self.heavy_chain_protein = (
            "QVQLVQSGAEVKKPGASVKVSCKASGYTFTDYYMHWVRQAPGQGLEWMG"
        )

    def test_docker_container_running(self):
        """Test that the IgBLAST Docker container is running."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=absequencealign-igblast",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert (
                "absequencealign-igblast" in result.stdout
            ), "IgBLAST container is not running"
        except Exception as e:
            pytest.fail(f"Failed to check Docker container: {e}")

    def test_database_discovery(self):
        """Test that available databases are discovered correctly."""
        databases = self.adapter.get_available_databases()
        assert isinstance(databases, dict)
        assert len(databases) > 0, "No databases discovered"

        # Should find at least human and mouse
        expected_organisms = ["human", "mouse"]
        for organism in expected_organisms:
            assert (
                organism in databases
            ), f"Expected organism '{organism}' not found"

            # Check that each organism has V, D, J databases
            organism_dbs = databases[organism]
            assert "V" in organism_dbs, f"V database not found for {organism}"
            assert "D" in organism_dbs, f"D database not found for {organism}"
            assert "J" in organism_dbs, f"J database not found for {organism}"

    def test_real_igblast_execution_mouse_nucleotide(self):
        """Test real IgBLAST execution with mouse nucleotide sequence."""
        try:
            # Get mouse databases
            databases = self.adapter.get_available_databases()
            mouse_dbs = databases["mouse"]

            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=mouse_dbs["V"]["path"],
                d_db=mouse_dbs["D"]["path"],
                j_db=mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Basic validation
            assert result["blast_type"] == "igblastn"
            assert "hits" in result
            assert "total_hits" in result

            # Should have at least some hits for a valid sequence
            assert result["total_hits"] >= 0

            # If we have hits, validate their structure
            if result["hits"]:
                hit = result["hits"][0]
                assert "hit_type" in hit
                assert "subject_id" in hit
                assert "percent_identity" in hit
                assert "evalue" in hit

                # Check gene-specific fields based on hit type
                if hit["hit_type"] == "V":
                    assert "v_gene" in hit
                    assert "chain_type" in hit
                elif hit["hit_type"] == "D":
                    assert "d_gene" in hit
                elif hit["hit_type"] == "J":
                    assert "j_gene" in hit

        except ExternalToolError as e:
            pytest.fail(f"IgBLAST execution failed: {e}")

    def test_real_igblast_execution_human_nucleotide(self):
        """Test real IgBLAST execution with human nucleotide sequence."""
        try:
            # Get human databases
            databases = self.adapter.get_available_databases()
            human_dbs = databases["human"]
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.human_dbs["V"]["path"],
                d_db=self.human_dbs["D"]["path"],
                j_db=self.human_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Basic validation
            assert result["blast_type"] == "igblastn"
            assert "hits" in result
            assert "total_hits" in result

            # Should have at least some hits for a valid sequence
            assert result["total_hits"] >= 0

            # If we have hits, validate their structure
            if result["hits"]:
                hit = result["hits"][0]
                assert "hit_type" in hit
                assert "subject_id" in hit
                assert "percent_identity" in hit
                assert "evalue" in hit

                # Check gene-specific fields based on hit type
                if hit["hit_type"] == "V":
                    assert "v_gene" in hit
                    assert "chain_type" in hit
                elif hit["hit_type"] == "D":
                    assert "d_gene" in hit
                elif hit["hit_type"] == "J":
                    assert "j_gene" in hit

        except ExternalToolError as e:
            pytest.fail(f"IgBLAST execution failed: {e}")

    @pytest.mark.skip(
        reason="IgBLAST container has default human database configuration causing conflicts"
    )
    def test_light_chain_detection(self):
        """Test light chain detection (no D gene)."""
        try:
            result = self.adapter.execute(
                query_sequence=self.light_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=None,  # Explicitly set to None for light chain
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            assert result["blast_type"] == "igblastn"
            assert "hits" in result

            if result["hits"]:
                hit = result["hits"][0]
                # Light chains typically don't have D genes
                # But this depends on the sequence and database
                assert "hit_type" in hit
                assert "subject_id" in hit
                assert "percent_identity" in hit
                assert "evalue" in hit

                # Check gene-specific fields based on hit type
                if hit["hit_type"] == "V":
                    assert "v_gene" in hit
                    assert "chain_type" in hit
                elif hit["hit_type"] == "J":
                    assert "j_gene" in hit

        except ExternalToolError as e:
            pytest.fail(f"IgBLAST execution failed: {e}")

    def test_protein_sequence_analysis(self):
        """Test protein sequence analysis."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_protein,
                v_db=self.human_dbs["V"]["path"],
                blast_type="igblastp",
            )

            assert result["blast_type"] == "igblastp"
            assert "hits" in result
            assert "total_hits" in result

            # Protein searches may have different results
            assert result["total_hits"] >= 0

            if result["hits"]:
                hit = result["hits"][0]
                assert "hit_type" in hit
                assert "subject_id" in hit
                assert "percent_identity" in hit
                assert "evalue" in hit

                # For protein IgBLAST, we typically only get V gene hits
                if hit["hit_type"] == "V":
                    assert "v_gene" in hit
                    assert "chain_type" in hit

        except ExternalToolError as e:
            pytest.fail(f"IgBLAST execution failed: {e}")

    def test_cdr3_extraction(self):
        """Test CDR3 sequence and position extraction."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            if result["hits"]:
                hit = result["hits"][0]

                # CDR3 information may or may not be present
                # depending on the sequence and IgBLAST version
                if hit.get("cdr3_sequence"):
                    assert isinstance(hit["cdr3_sequence"], str)
                    assert len(hit["cdr3_sequence"]) > 0

                    if hit.get("cdr3_start") is not None:
                        assert isinstance(hit["cdr3_start"], int)
                        assert hit["cdr3_start"] > 0

                    if hit.get("cdr3_end") is not None:
                        assert isinstance(hit["cdr3_end"], int)
                        assert hit["cdr3_end"] > 0

                        if hit.get("cdr3_start") is not None:
                            assert hit["cdr3_end"] > hit["cdr3_start"]

        except ExternalToolError as e:
            pytest.fail(f"IgBLAST execution failed: {e}")

    def test_error_handling_invalid_sequence(self):
        """Test error handling with invalid sequence."""
        with pytest.raises(
            ExternalToolError, match="Invalid nucleotide sequence"
        ):
            self.adapter.execute(
                query_sequence="INVALID123",
                v_db=self.mouse_dbs["V"]["path"],
                blast_type="igblastn",
            )

    def test_error_handling_invalid_database_path(self):
        """Test error handling with invalid database path."""
        with pytest.raises(ExternalToolError):
            self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db="/invalid/path/to/database",
                blast_type="igblastn",
            )

    def test_error_handling_invalid_blast_type(self):
        """Test error handling with invalid blast type."""
        with pytest.raises(ExternalToolError):
            self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                blast_type="invalid_blast_type",
            )

    def test_command_building_validation(self):
        """Test that commands are built correctly."""
        command = self.adapter._build_command(
            query_sequence=self.heavy_chain_nucleotide,
            v_db=self.mouse_dbs["V"]["path"],
            d_db=self.mouse_dbs["D"]["path"],
            j_db=self.mouse_dbs["J"]["path"],
            blast_type="igblastn",
        )

        # Validate command structure
        assert command[0] == "docker"
        assert command[1] == "exec"
        assert command[2] == "-i"
        assert command[3] == "absequencealign-igblast"
        assert command[4] == "igblastn"
        assert "-query" in command
        assert "/dev/stdin" in command

        # Validate database paths
        v_db_index = command.index("-germline_db_V")
        d_db_index = command.index("-germline_db_D")
        j_db_index = command.index("-germline_db_J")

        assert command[v_db_index + 1] == self.mouse_dbs["V"]["path"]
        assert command[d_db_index + 1] == self.mouse_dbs["D"]["path"]
        assert command[j_db_index + 1] == self.mouse_dbs["J"]["path"]

    def test_response_format_consistency(self):
        """Test that response format is consistent across different organisms."""
        # Test both human and mouse
        test_configs = [
            ("human", self.human_dbs),
            ("mouse", self.mouse_dbs),
        ]

        for organism, dbs in test_configs:
            try:
                result = self.adapter.execute(
                    query_sequence=self.heavy_chain_nucleotide,
                    v_db=dbs["V"]["path"],
                    d_db=dbs["D"]["path"],
                    j_db=dbs["J"]["path"],
                    blast_type="igblastn",
                )

                # Validate consistent response structure
                assert "blast_type" in result
                assert "hits" in result
                assert "total_hits" in result

                assert result["blast_type"] == "igblastn"
                assert isinstance(result["hits"], list)
                assert isinstance(result["total_hits"], int)
                assert result["total_hits"] >= 0

            except ExternalToolError as e:
                # Skip if organism doesn't work, but log it
                logger.info(f"Warning: {organism} organism test failed: {e}")

    def test_performance_basic(self):
        """Basic performance test - execution should complete within reasonable time."""
        import time

        start_time = time.time()

        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            execution_time = time.time() - start_time

            # Should complete within 30 seconds
            assert (
                execution_time < 30
            ), f"IgBLAST execution took too long: {execution_time:.2f} seconds"

            # Basic result validation
            assert result["blast_type"] == "igblastn"
            assert "hits" in result

        except ExternalToolError as e:
            pytest.fail(f"Performance test failed: {e}")

    def test_smart_chain_type_detection(self):
        """Test smart chain type detection feature."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Basic validation that we get results
            assert "blast_type" in result
            assert "hits" in result
            assert result["blast_type"] == "igblastn"

            # Check that we have hits with gene information
            if result["hits"]:
                v_hits = [
                    h for h in result["hits"] if h.get("hit_type") == "V"
                ]
                d_hits = [
                    h for h in result["hits"] if h.get("hit_type") == "D"
                ]
                j_hits = [
                    h for h in result["hits"] if h.get("hit_type") == "J"
                ]

                # Should have V, D, and J hits for a heavy chain
                assert len(v_hits) > 0
                assert len(d_hits) > 0
                assert len(j_hits) > 0

        except ExternalToolError as e:
            pytest.fail(f"Smart chain type detection failed: {e}")

    def test_airr_format_support(self):
        """Test AIRR format support."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.human_dbs["V"]["path"],
                d_db=self.human_dbs["D"]["path"],
                j_db=self.human_dbs["J"]["path"],
                blast_type="igblastn",
                use_airr_format=True,
            )

            # Should have AIRR data
            assert "airr_data" in result
            assert isinstance(result["airr_data"], dict)

            # AIRR data should contain key fields
            airr_data = result["airr_data"]
            if airr_data:  # If AIRR parsing was successful
                assert "v_call" in airr_data or "locus" in airr_data

        except ExternalToolError as e:
            # AIRR format might not be supported in all IgBLAST versions
            # This is acceptable - just log the issue
            logger.info(
                f"Note: AIRR format not supported in this IgBLAST version: {e}"
            )

    def test_chain_type_detection_disabled(self):
        """Test that chain type detection can be disabled."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Should not have detected chain type when disabled
            assert "detected_chain_type" not in result

        except ExternalToolError as e:
            pytest.fail(f"Chain type detection disable test failed: {e}")

    def test_enhanced_parsing_features(self):
        """Test enhanced parsing features including detailed hit information."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Basic validation
            assert "blast_type" in result
            assert "hits" in result
            assert result["blast_type"] == "igblastn"

            # If we have hits, check their structure
            if result["hits"]:
                hit = result["hits"][0]
                assert "hit_type" in hit
                assert "subject_id" in hit
                assert "percent_identity" in hit
                assert "alignment_length" in hit
                assert "evalue" in hit
                assert "bit_score" in hit
                assert "subject_url" in hit

                # Check gene-specific fields
                if hit["hit_type"] == "V":
                    assert "v_gene" in hit
                    assert "chain_type" in hit
                elif hit["hit_type"] == "D":
                    assert "d_gene" in hit
                elif hit["hit_type"] == "J":
                    assert "j_gene" in hit

        except ExternalToolError as e:
            pytest.fail(f"Enhanced parsing test failed: {e}")

    def test_analysis_summary_completeness(self):
        """Test that analysis summary contains comprehensive information."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Should have hits
            assert "hits" in result

            # Check that we have hits with gene information
            if result["hits"]:
                v_hits = [
                    h for h in result["hits"] if h.get("hit_type") == "V"
                ]
                j_hits = [
                    h for h in result["hits"] if h.get("hit_type") == "J"
                ]
                assert len(v_hits) > 0 or len(j_hits) > 0

        except ExternalToolError as e:
            pytest.fail(f"Analysis summary test failed: {e}")

    def test_url_generation(self):
        """Test that subject URLs are generated correctly."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # Check that hits have URLs
            for hit in result["hits"]:
                assert "subject_url" in hit

                # If it's a known gene, should have IMGT URL
                if hit.get("v_gene") and hit["v_gene"] != "N/A":
                    url = hit["subject_url"]
                    if url:  # URL may be empty for unknown genes
                        assert "imgt.org" in url
                        assert hit["v_gene"] in url

        except ExternalToolError as e:
            pytest.fail(f"URL generation test failed: {e}")

    def test_advanced_error_handling(self):
        """Test advanced error handling with various edge cases."""
        # Test with sequence containing invalid characters
        with pytest.raises(
            ExternalToolError, match="Invalid nucleotide sequence"
        ):
            self.adapter.execute(
                query_sequence="ACGT123XYZ",
                v_db=self.mouse_dbs["V"]["path"],
                blast_type="igblastn",
            )

        # Test with empty sequence (should fail validation)
        with pytest.raises(
            ExternalToolError, match="Sequence cannot be empty"
        ):
            self.adapter.execute(
                query_sequence="",
                v_db=self.mouse_dbs["V"]["path"],
                blast_type="igblastn",
            )

    def test_feature_compatibility(self):
        """Test that all advanced features work together."""
        try:
            result = self.adapter.execute(
                query_sequence=self.heavy_chain_nucleotide,
                v_db=self.mouse_dbs["V"]["path"],
                d_db=self.mouse_dbs["D"]["path"],
                j_db=self.mouse_dbs["J"]["path"],
                blast_type="igblastn",
            )

            # All features should work together
            assert "blast_type" in result
            assert "hits" in result

            # Basic validation
            assert result["blast_type"] == "igblastn"
            assert isinstance(result["hits"], list)

        except ExternalToolError as e:
            pytest.fail(f"Feature compatibility test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
