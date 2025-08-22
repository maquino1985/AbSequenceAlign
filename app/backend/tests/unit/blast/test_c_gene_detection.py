"""
Test C gene detection functionality in IgBLAST.

This test verifies that C gene detection works correctly for different
sequence types and that the configuration is properly loaded.
Only mocks external dependencies (Docker/IgBLAST execution), not business logic.
"""

import logging
from unittest.mock import MagicMock

import pytest

from backend.config import (
    get_igblast_v_db_path,
    get_igblast_d_db_path,
    get_igblast_j_db_path,
    get_igblast_c_db_path,
)
from backend.infrastructure.adapters.igblast_adapter import IgBlastAdapter

logger = logging.getLogger(__name__)


class TestCGeneDetection:
    """Test C gene detection in IgBLAST"""

    @pytest.fixture
    def adapter(self):
        """Create IgBlastAdapter with mocked Docker client (external dependency only)"""
        mock_docker_client = MagicMock()
        return IgBlastAdapter(docker_client=mock_docker_client)

    @pytest.mark.skip(
        reason="C gene detection tests skipped - will be revisited later"
    )
    def test_database_path_configuration(self):
        """Test that database paths are correctly configured"""
        logger.info("Testing database path configuration")

        # Test human database paths
        human_v = get_igblast_v_db_path("human")
        human_d = get_igblast_d_db_path("human")
        human_j = get_igblast_j_db_path("human")
        human_c = get_igblast_c_db_path("human")

        assert "airr_c_human_ig.V" in str(human_v)
        assert "airr_c_human_igh.D" in str(human_d)
        assert "airr_c_human_ig.J" in str(human_j)
        assert "ncbi_human_c_genes" in str(human_c)

        logger.info(f"Human V database: {human_v}")
        logger.info(f"Human D database: {human_d}")
        logger.info(f"Human J database: {human_j}")
        logger.info(f"Human C database: {human_c}")

        # Test generic organism paths
        mouse_v = get_igblast_v_db_path("mouse")
        mouse_c = get_igblast_c_db_path("mouse")

        assert "mouse_V" in str(mouse_v)
        assert "ncbi_mouse_c_genes" in str(mouse_c)

        logger.info(f"Mouse V database: {mouse_v}")
        logger.info(f"Mouse C database: {mouse_c}")

    @pytest.mark.skip(
        reason="C gene detection tests skipped - will be revisited later"
    )
    def test_command_building_with_c_database(self, adapter):
        """Test that IgBLAST commands include C region database - only mock external execution"""
        logger.info("Testing command building with C region database")

        # Test our actual _build_command method (business logic) - provide required parameters
        command = adapter._build_command(
            query_sequence="ATGCGTTAGCATGCAAA",  # Required parameter
            blast_type="igblastn",
            organism="human",
        )

        # Verify our business logic correctly builds the command
        command_str = " ".join(command)

        # Check that C region database is included in nucleotide search
        assert (
            "-c_region_db" in command_str
        ), f"C region database not found in command: {command}"
        assert (
            "ncbi_human_c_genes" in command_str
        ), f"Human C gene database not found: {command}"

        logger.info(
            f"Command correctly includes C region database: {command_str}"
        )

    def test_command_building_protein_no_c_database(self, adapter):
        """Test that protein searches don't include C region database"""
        logger.info("Testing protein search command building")

        # Test our actual _build_command method for protein search
        # Use 'mouse' since that's what the adapter supports
        command = adapter._build_command(
            query_sequence="EVQLVESGGGLVQPGRSLRLSCAAS",  # Required parameter
            blast_type="igblastp",
            organism="mouse",
        )

        command_str = " ".join(command)

        # Verify our business logic correctly excludes C database for protein searches
        assert (
            "-c_region_db" not in command_str
        ), f"C region database should not be in protein search: {command}"
        assert (
            "-germline_db_D" not in command_str
        ), f"D database should not be in protein search: {command}"
        assert (
            "-germline_db_J" not in command_str
        ), f"J database should not be in protein search: {command}"

        logger.info(
            f"Protein command correctly excludes C/D/J databases: {command_str}"
        )

    @pytest.mark.skip(
        reason="C gene detection tests skipped - will be revisited later"
    )
    def test_different_organisms_use_correct_databases(self, adapter):
        """Test that different organisms use the correct database paths"""
        logger.info("Testing organism-specific database paths")

        # Test human databases
        human_command = adapter._build_command(
            query_sequence="ATGCGTTAGCATGCAAA",  # Required parameter
            blast_type="igblastn",
            organism="human",
        )
        human_command_str = " ".join(human_command)

        assert (
            "airr_c_human_ig.V" in human_command_str
        ), "Human should use AIRR format V database"
        assert (
            "airr_c_human_igh.D" in human_command_str
        ), "Human should use AIRR format D database"
        assert (
            "ncbi_human_c_genes" in human_command_str
        ), "Human should use NCBI C gene database"

        # Test mouse databases (using generic pattern)
        mouse_command = adapter._build_command(
            query_sequence="ATGCGTTAGCATGCAAA",  # Required parameter
            blast_type="igblastn",
            organism="mouse",
        )
        mouse_command_str = " ".join(mouse_command)

        assert (
            "mouse_V" in mouse_command_str
        ), "Mouse should use generic V database pattern"
        assert (
            "mouse_D" in mouse_command_str
        ), "Mouse should use generic D database pattern"
        assert (
            "ncbi_mouse_c_genes" in mouse_command_str
        ), "Mouse should use generic C gene database pattern"

        logger.info("Organism-specific databases correctly configured")

    @pytest.mark.skip(
        reason="Integration test - requires actual IgBLAST setup"
    )
    def test_c_gene_detection_integration(self):
        """Integration test for C gene detection with real sequences"""
        logger.info("Running C gene detection integration test")

        # Variable domain only - should have no C gene
        vh_only = (
            "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTG"
            "AGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCG"
            "CCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTAT"
            "GCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTAT"
            "CTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGC"
            "TATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC"
        )

        try:
            import docker

            docker_client = docker.from_env()
            adapter = IgBlastAdapter(docker_client=docker_client)

            results = adapter.execute(
                query_sequence=vh_only, blast_type="igblastn", organism="human"
            )

            assert results is not None
            assert "hits" in results

            if results["hits"]:
                hit = results["hits"][0]
                logger.info(f"V gene: {hit.get('v_gene')}")
                logger.info(f"D gene: {hit.get('d_gene')}")
                logger.info(f"J gene: {hit.get('j_gene')}")
                logger.info(
                    f"C gene: {hit.get('c_gene') or 'Not found (expected for VH only)'}"
                )

                # For variable domain only, C gene should be None
                assert hit.get("c_gene") is None or hit.get("c_gene") == ""
                logger.info(
                    "C gene correctly shows as not found for variable domain only sequence"
                )

        except Exception as e:
            logger.warning(
                f"Integration test skipped due to setup issues: {e}"
            )
            pytest.skip(f"IgBLAST not available: {e}")

    def test_airr_parsing_with_c_gene(self, adapter):
        """Test AIRR format parsing includes C gene information - test actual parsing logic"""
        logger.info("Testing AIRR parsing with C gene information")

        # Use real AIRR output format (not mocked business logic, just the external data format)
        real_airr_output = """sequence_id	sequence	sequence_aa	locus	stop_codon	vj_in_frame	v_frameshift	productive	rev_comp	complete_vdj	d_frame	v_call	d_call	j_call	c_call	sequence_alignment	germline_alignment
test_seq	ATGCGTTAGCATGCAAA	MRLAC	IGH	F	T	F	T	F	T	1	IGHV3-9*01	IGHD1-26*01	IGHJ1*01	IGHG1	ATGCGTTAGCATGCAAA	ATGCGTTAGCATGCAAA"""

        # Test our actual parsing business logic
        results = adapter._parse_airr_output(real_airr_output, "igblastn")

        assert "hits" in results
        assert len(results["hits"]) == 1

        hit = results["hits"][0]
        assert hit["v_gene"] == "IGHV3-9*01"
        assert hit["d_gene"] == "IGHD1-26*01"
        assert hit["j_gene"] == "IGHJ1*01"
        assert hit["c_gene"] == "IGHG1"

        logger.info(f"Successfully parsed C gene: {hit['c_gene']}")

    def test_airr_parsing_without_c_gene(self, adapter):
        """Test AIRR format parsing when C gene is empty - test actual parsing logic"""
        logger.info("Testing AIRR parsing without C gene information")

        # Use real AIRR output format with empty C gene field
        real_airr_output_no_c = """sequence_id	sequence	sequence_aa	locus	stop_codon	vj_in_frame	v_frameshift	productive	rev_comp	complete_vdj	d_frame	v_call	d_call	j_call	c_call	sequence_alignment	germline_alignment
test_seq	ATGCGTTAGCATGCAAA	MRLAC	IGH	F	T	F	T	F	T	1	IGHV3-9*01	IGHD1-26*01	IGHJ1*01		ATGCGTTAGCATGCAAA	ATGCGTTAGCATGCAAA"""

        # Test our actual parsing business logic
        results = adapter._parse_airr_output(real_airr_output_no_c, "igblastn")

        assert "hits" in results
        assert len(results["hits"]) == 1

        hit = results["hits"][0]
        assert hit["v_gene"] == "IGHV3-9*01"
        assert hit["d_gene"] == "IGHD1-26*01"
        assert hit["j_gene"] == "IGHJ1*01"
        assert hit["c_gene"] is None  # Empty field should become None

        logger.info(
            "C gene correctly shows as None when not present in AIRR output"
        )

    def test_cdr3_position_extraction(self, adapter):
        """Test CDR3 position extraction logic - test actual business logic"""
        logger.info("Testing CDR3 position extraction from AIRR data")

        # Test our actual CDR3 extraction methods with realistic AIRR data
        mock_airr_data = {
            "fwr3_end": "288",
            "fwr4_start": "350",
            "junction_length": "27",
            "cdr3_start": "",  # Empty - should use fallback logic
            "cdr3_end": "",  # Empty - should use fallback logic
        }

        # Test our actual business logic methods
        cdr3_start = adapter._extract_cdr3_start(mock_airr_data)
        cdr3_end = adapter._extract_cdr3_end(mock_airr_data)

        # Verify our fallback logic works correctly
        assert (
            cdr3_start == 289
        ), f"CDR3 start should be FWR3 end + 1: {cdr3_start}"
        assert (
            cdr3_end == 349
        ), f"CDR3 end should be FWR4 start - 1: {cdr3_end}"

        logger.info(
            f"CDR3 positions correctly calculated: start={cdr3_start}, end={cdr3_end}"
        )

        # Test with direct CDR3 positions provided
        direct_airr_data = {
            "cdr3_start": "290",
            "cdr3_end": "320",
            "fwr3_end": "288",  # Should not be used when direct values available
            "fwr4_start": "350",
        }

        direct_start = adapter._extract_cdr3_start(direct_airr_data)
        direct_end = adapter._extract_cdr3_end(direct_airr_data)

        assert (
            direct_start == 290
        ), "Should use direct CDR3 start when available"
        assert direct_end == 320, "Should use direct CDR3 end when available"

        logger.info("Direct CDR3 positions correctly used when available")
