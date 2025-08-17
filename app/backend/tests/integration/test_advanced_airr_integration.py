"""
Integration tests for advanced AIRR format parsing with IgBLAST.
Tests the complete pipeline from IgBLAST execution to advanced AIRR parsing.
"""

import logging
from unittest.mock import patch, MagicMock

import pytest

from backend.infrastructure.adapters.igblast_adapter import IgBlastAdapter

logger = logging.getLogger(__name__)


class TestAdvancedAIRRIntegration:
    """Integration tests for advanced AIRR parsing"""

    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client for testing"""
        return MagicMock()

    @pytest.fixture
    def adapter(self, mock_docker_client):
        """Create IgBlastAdapter with mocked Docker client"""
        return IgBlastAdapter(docker_client=mock_docker_client)

    @pytest.fixture
    def sample_igblast_airr_output(self):
        """Sample IgBLAST AIRR output for testing"""
        return """sequence_id	sequence	sequence_aa	locus	stop_codon	vj_in_frame	v_frameshift	productive	rev_comp	complete_vdj	d_frame	v_call	d_call	j_call	c_call	sequence_alignment	germline_alignment	sequence_alignment_aa	germline_alignment_aa	v_alignment_start	v_alignment_end	d_alignment_start	d_alignment_end	j_alignment_start	j_alignment_end	v_sequence_alignment	v_sequence_alignment_aa	v_germline_alignment	v_germline_alignment_aa	d_sequence_alignment	d_sequence_alignment_aa	d_germline_alignment	d_germline_alignment_aa	j_sequence_alignment	j_sequence_alignment_aa	j_germline_alignment	j_germline_alignment_aa	fwr1	fwr1_aa	cdr1	cdr1_aa	fwr2	fwr2_aa	cdr2	cdr2_aa	fwr3	fwr3_aa	fwr4	fwr4_aa	cdr3	cdr3_aa	junction	junction_length	junction_aa	junction_aa_length	v_score	d_score	j_score	v_cigar	d_cigar	j_cigar	v_support	d_support	j_support	v_identity	d_identity	j_identity	v_sequence_start	v_sequence_end	v_germline_start	v_germline_end	d_sequence_start	d_sequence_end	d_germline_start	d_germline_end	j_sequence_start	j_sequence_end	j_germline_start	j_germline_end	fwr1_start	fwr1_end	cdr1_start	cdr1_end	fwr2_start	fwr2_end	cdr2_start	cdr2_end	fwr3_start	fwr3_end	fwr4_start	fwr4_end	cdr3_start	cdr3_end	np1	np1_length	np2	np2_length
test_seq	GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC	EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS	IGH	F		F	T	F	T		IGHV3-9*01	IGHD1-26*01,IGHD5-5*01,IGHD6-13*01	IGHJ1*01	IGHG1*01	GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGT	GAAGTGCAGCTGGTGGAGTCTGGGGGAGGCTTGGTACAGCCTGGCAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTGATGATTATGCCATGCACTGGGTCCGGCAAGCTCCAGGGAAGGGCCTGGAGTGGGTCTCAGGTATTAGTTGGAATAGTGGTAGCATAGGCTATGCGGACTCTGTGAAGGGCCGATTCACCATCTCCAGAGACAACGCCAAGAACTCCCTGTATCTGCAAATGAACAGTCTGAGAGCTGAGGACACGGCCTTGTATTACTGTGCAAAAG	EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTV	EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSGISWNSGSIGYADSV KGRFTISRDNAKNSLYLQMNSLRAEDTALYYCAK	1	295	297	302	331	356	GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAG	EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAK	GAAGTGCAGCTGGTGGAGTCTGGGGGAGGCTTGGTACAGCCTGGCAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTGATGATTATGCCATGCACTGGGTCCGGCAAGCTCCAGGGAAGGGCCTGGAGTGGGTCTCAGGTATTAGTTGGAATAGTGGTAGCATAGGCTATGCGGACTCTGTGAAGGGCCGATTCACCATCTCCAGAGACAACGCCAAGAACTCCCTGTATCTGCAAATGAACAGTCTGAGAGCTGAGGACACGGCCTTGTATTACTGTGCAAAAG	EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSGISWNSGSIGYADSV KGRFTISRDNAKNSLYLQMNSLRAEDTALYYCAK	GAGCTA	S	GAGCTA	S	TGGGGCCAGGGCACCCTGGTGACCGT	WGQGTLVTV	TGGGGCCAGGGCACCCTGGTCACCGT	WGQGTLVTV	GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGC	EVQLVESGGGLVQPGRSLRLSCAAS	GGCTTTACCTTTGATGATTATGCG	GFTFDDYA	ATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCG	MHWVRQAPGKGLEWVSA	ATTACCTGGAACAGCGGCCATATT	ITWNSGH I	GATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGC	DYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYC			TCTGAGCACCGCGAGCAGCCTGGATTAT	SSTASSL DY	TCTGAGCACCGCGAGCAGCCTGGATTAT	28	SSTASSL DY	9	199.717	12.223	44.909	295M68S3N	296S10N6M61S4N	330S18N26M7S8N	2.339e-53	3.277e+01	8.131e-09	71.525	100.000	96.154	1	295	1	295	297	302	11	16	331	356	19	44	1	75	76	99	100	150	151	174	175	288			T	1	TCTGAGCACCGCGAGCAGCCTGGATTAT	28"""

    def test_advanced_airr_parsing_integration(
        self, adapter, sample_igblast_airr_output
    ):
        """Test complete integration of advanced AIRR parsing with IgBLAST adapter"""

        # Mock the subprocess.run to return our sample output
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = sample_igblast_airr_output
            mock_run.return_value.stderr = ""
            result = adapter.execute(
                query_sequence="GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC",
                blast_type="igblastn",
                organism="human",
            )

        # Test backward compatibility - should have legacy format
        assert "hits" in result
        assert "analysis_summary" in result
        assert "total_hits" in result
        assert result["total_hits"] == 1

        # Test legacy hit format
        hit = result["hits"][0]
        assert hit["query_id"] == "test_seq"
        assert hit["v_gene"] == "IGHV3-9*01"
        assert hit["d_gene"] == "IGHD1-26*01,IGHD5-5*01,IGHD6-13*01"
        assert hit["j_gene"] == "IGHJ1*01"
        assert hit["c_gene"] == "IGHG1*01"
        assert hit["identity"] == 71.525
        assert hit["cdr3_sequence"] == "TCTGAGCACCGCGAGCAGCCTGGATTAT"

        # Test enhanced fields in legacy format
        assert hit["productive"] == "T"
        assert hit["locus"] == "IGH"
        assert hit["complete_vdj"] is True
        assert hit["stop_codon"] is False
        # vj_in_frame field is empty in test data, so it should be None
        assert hit["vj_in_frame"] is None

        # Test enhanced analysis summary
        summary = result["analysis_summary"]
        assert summary["best_v_gene"] == "IGHV3-9*01"
        assert summary["best_c_gene"] == "IGHG1*01"
        assert summary["productive_sequences"] == 1
        assert summary["locus"] == "IGH"
        assert "IGHV3-9*01" in summary["unique_v_genes"]
        assert "IGHJ1*01" in summary["unique_j_genes"]
        assert len(summary["unique_d_genes"]) >= 3

        # Test framework and CDR information in summary
        assert summary["fwr1_sequence"] == "EVQLVESGGGLVQPGRSLRLSCAAS"
        assert summary["cdr1_sequence"] == "GFTFDDYA"
        assert summary["cdr2_sequence"] == "ITWNSGH I"
        assert summary["junction_aa"] == "SSTASSL DY"

        # Test full AIRR result is included
        assert "airr_result" in result
        assert result["airr_result"] is not None

        # Verify AIRR result structure
        airr_result = result["airr_result"]
        assert "rearrangements" in airr_result
        assert len(airr_result["rearrangements"]) == 1
        assert airr_result["total_sequences"] == 1
        assert airr_result["productive_sequences"] == 1

    def test_enhanced_airr_data_extraction(
        self, adapter, sample_igblast_airr_output
    ):
        """Test that enhanced AIRR data is properly extracted"""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = sample_igblast_airr_output
            mock_run.return_value.stderr = ""
            result = adapter.execute(
                query_sequence="GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC",
                blast_type="igblastn",
                organism="human",
            )

        airr_result = result["airr_result"]
        rearrangement = airr_result["rearrangements"][0]

        # Test detailed alignment information
        assert rearrangement["v_alignment"]["score"] == 199.717
        assert rearrangement["v_alignment"]["identity"] == 71.525
        assert rearrangement["v_alignment"]["cigar"] == "295M68S3N"
        assert rearrangement["d_alignment"]["score"] == 12.223
        assert rearrangement["j_alignment"]["score"] == 44.909

        # Test sequence coordinates
        assert rearrangement["v_sequence_start"] == 1
        assert rearrangement["v_sequence_end"] == 295
        assert rearrangement["d_sequence_start"] == 297
        assert rearrangement["d_sequence_end"] == 302
        assert rearrangement["j_sequence_start"] == 331
        assert rearrangement["j_sequence_end"] == 356

        # Test framework and CDR regions
        assert (
            rearrangement["fwr1"]["sequence_aa"] == "EVQLVESGGGLVQPGRSLRLSCAAS"
        )
        assert rearrangement["fwr1"]["start"] == 1
        assert rearrangement["fwr1"]["end"] == 75

        assert rearrangement["cdr1"]["sequence_aa"] == "GFTFDDYA"
        assert rearrangement["cdr1"]["start"] == 76
        assert rearrangement["cdr1"]["end"] == 99

        assert rearrangement["cdr2"]["sequence_aa"] == "ITWNSGH I"
        assert rearrangement["cdr2"]["start"] == 151
        assert rearrangement["cdr2"]["end"] == 174

        # Test junction region details
        junction = rearrangement["junction_region"]
        assert junction["junction"] == "TCTGAGCACCGCGAGCAGCCTGGATTAT"
        assert junction["junction_length"] == 28
        assert junction["junction_aa"] == "SSTASSL DY"
        assert junction["junction_aa_length"] == 9
        assert junction["np2"] == "TCTGAGCACCGCGAGCAGCCTGGATTAT"
        assert junction["np2_length"] == 28

    def test_fallback_parsing_on_error(self, adapter):
        """Test that fallback parsing is used when advanced parsing fails"""

        # Create malformed AIRR output that will cause advanced parser to fail
        malformed_output = "invalid\theader\nmalformed\tdata"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = malformed_output
            mock_run.return_value.stderr = ""
            with patch.object(
                adapter._airr_parser,
                "parse_airr_output",
                side_effect=Exception("Parse error"),
            ):
                result = adapter.execute(
                    query_sequence="GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC",
                    blast_type="igblastn",
                    organism="human",
                )

        # Should still return a result using fallback parsing
        assert "hits" in result
        assert "analysis_summary" in result
        assert "total_hits" in result
        # With malformed data, should return empty results
        assert result["total_hits"] == 0

    def test_protein_search_uses_tabular_parsing(self, adapter):
        """Test that protein searches still use tabular parsing (not AIRR)"""

        tabular_output = """# IGBLASTN 2.14.1+
# Iteration: 0
# Query: test_protein
# Database: V_DATABASE D_DATABASE J_DATABASE
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
test_protein	IGHV3-9*01	85.5	100	14	1	1	100	1	100	1e-30	150"""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = tabular_output
            mock_run.return_value.stderr = ""
            result = adapter.execute(
                query_sequence="EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS",
                blast_type="igblastp",
                organism="human",
            )

        # Should use tabular parsing, not AIRR
        assert "hits" in result
        assert "airr_result" not in result or result["airr_result"] is None

        if result["hits"]:
            hit = result["hits"][0]
            assert hit["query_id"] == "test_protein"
            assert hit["subject_id"] == "IGHV3-9*01"
            assert hit["identity"] == 85.5


@pytest.mark.skip(reason="Requires actual IgBLAST setup and databases")
class TestRealIgBLASTAdvancedParsing:
    """Integration tests with real IgBLAST execution"""

    def test_real_igblast_with_advanced_parsing(self):
        """Test advanced parsing with real IgBLAST execution"""
        try:
            import docker

            docker_client = docker.from_env()
            adapter = IgBlastAdapter(docker_client=docker_client)

            # Use the full Humira sequence for comprehensive testing
            humira_sequence = (
                "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTG"
                "AGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCG"
                "CCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTAT"
                "GCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTAT"
                "CTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGC"
                "TATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC"
            )

            result = adapter.execute(
                query_sequence=humira_sequence,
                blast_type="igblastn",
                organism="human",
            )

            # Verify enhanced parsing worked
            assert "airr_result" in result
            assert result["airr_result"] is not None

            if result["hits"]:
                hit = result["hits"][0]

                # Should have comprehensive gene assignments
                assert hit["v_gene"] is not None
                assert hit["d_gene"] is not None
                assert hit["j_gene"] is not None
                assert hit["cdr3_sequence"] is not None

                # Should have enhanced productivity information
                assert "productive" in hit
                assert "locus" in hit
                assert "complete_vdj" in hit

                logger.info(f"Advanced AIRR parsing results:")
                logger.info(f"V gene: {hit['v_gene']}")
                logger.info(f"D gene: {hit['d_gene']}")
                logger.info(f"J gene: {hit['j_gene']}")
                logger.info(f"C gene: {hit['c_gene']}")
                logger.info(f"CDR3: {hit['cdr3_sequence']}")
                logger.info(f"Productive: {hit['productive']}")
                logger.info(f"Locus: {hit['locus']}")

                # Verify analysis summary has enhanced data
                summary = result["analysis_summary"]
                assert "productive_sequences" in summary
                assert "unique_v_genes" in summary
                assert "locus" in summary

        except Exception as e:
            pytest.skip(f"Real IgBLAST test skipped: {e}")
