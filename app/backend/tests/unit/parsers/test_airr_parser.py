"""
Tests for advanced AIRR format parser.
"""

import logging

import pytest

from backend.infrastructure.parsers.airr_parser import AIRRParser
from backend.models.airr_models import (
    AIRRAnalysisResult,
    AIRRRearrangement,
    Locus,
    ProductivityStatus,
)

logger = logging.getLogger(__name__)


class TestAIRRParser:
    """Test advanced AIRR format parsing"""

    @pytest.fixture
    def parser(self):
        """Create AIRR parser instance"""
        return AIRRParser()

    @pytest.fixture
    def sample_airr_output(self):
        """Sample AIRR format output for testing"""
        return """sequence_id\tsequence\tsequence_aa\tlocus\tstop_codon\tvj_in_frame\tv_frameshift\tproductive\trev_comp\tcomplete_vdj\td_frame\tv_call\td_call\tj_call\tsequence_alignment\tgermline_alignment\tsequence_alignment_aa\tgermline_alignment_aa\tv_alignment_start\tv_alignment_end\td_alignment_start\td_alignment_end\tj_alignment_start\tj_alignment_end\tv_sequence_alignment\tv_sequence_alignment_aa\tv_germline_alignment\tv_germline_alignment_aa\td_sequence_alignment\td_sequence_alignment_aa\td_germline_alignment\td_germline_alignment_aa\tj_sequence_alignment\tj_sequence_alignment_aa\tj_germline_alignment\tj_germline_alignment_aa\tfwr1\tfwr1_aa\tcdr1\tcdr1_aa\tfwr2\tfwr2_aa\tcdr2\tcdr2_aa\tfwr3\tfwr3_aa\tfwr4\tfwr4_aa\tcdr3\tcdr3_aa\tjunction\tjunction_length\tjunction_aa\tjunction_aa_length\tv_score\td_score\tj_score\tv_cigar\td_cigar\tj_cigar\tv_support\td_support\tj_support\tv_identity\td_identity\tj_identity\tv_sequence_start\tv_sequence_end\tv_germline_start\tv_germline_end\td_sequence_start\td_sequence_end\td_germline_start\td_germline_end\tj_sequence_start\tj_sequence_end\tj_germline_start\tj_germline_end\tfwr1_start\tfwr1_end\tcdr1_start\tcdr1_end\tfwr2_start\tfwr2_end\tcdr2_start\tcdr2_end\tfwr3_start\tfwr3_end\tfwr4_start\tfwr4_end\tcdr3_start\tcdr3_end\tnp1\tnp1_length\tnp2\tnp2_length
test_seq\tGAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC\tEVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS\tIGH\tF\t\t\tT\tF\tT\t\tIGHV3-9*01\tIGHD1-26*01,IGHD5-5*01,IGHD6-13*01\tIGHJ1*01\tGAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGT\tGAAGTGCAGCTGGTGGAGTCTGGGGGAGGCTTGGTACAGCCTGGCAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTGATGATTATGCCATGCACTGGGTCCGGCAAGCTCCAGGGAAGGGCCTGGAGTGGGTCTCAGGTATTAGTTGGAATAGTGGTAGCATAGGCTATGCGGACTCTGTGAAGGGCCGATTCACCATCTCCAGAGACAACGCCAAGAACTCCCTGTATCTGCAA\tEVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTV\tEVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSGISWNSGSIGYADSVKGRFTISRDNAKNSLYLQMNSLRAEDTALYYCAK\t1\t295\t297\t302\t331\t356\tGAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAA\tEVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAK\tGAAGTGCAGCTGGTGGAGTCTGGGGGAGGCTTGGTACAGCCTGGCAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTGATGATTATGCCATGCACTGGGTCCGGCAAGCTCCAGGGAAGGGCCTGGAGTGGGTCTCAGGTATTAGTTGGAATAGTGGTAGCATAGGCTATGCGGACTCTGTGAAGGGCCGATTCACCATCTCCAGAGACAACGCCAAGAACTCCCTGTATCTGCAA\tEVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSGISWNSGSIGYADSVKGRFTISRDNAKNSLYLQMNSLRAEDTALYYCAK\tGAGCTA\tS\tGAGCTA\tS\tTGGGGCCAGGGCACCCTGGTGACCGT\tWGQGTLVTV\tTGGGGCCAGGGCACCCTGGTCACCGT\tWGQGTLVTV\tGAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGC\tEVQLVESGGGLVQPGRSLRLSCAAS\tGGCTTTACCTTTGATGATTATGCG\tGFTFDDYA\tATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCG\tMHWVRQAPGKGLEWVSA\tATTACCTGGAACAGCGGCCATATT\tITWNSGHI\tGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGC\tDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYC\t\t\t\t\tTCTGAGCACCGCGAGCAGCCTGGATTAT\t28\tSSTASSLDY\t9\t199.717\t12.223\t44.909\t295M68S3N\t296S10N6M61S4N\t330S18N26M7S8N\t2.339e-53\t3.277e+01\t8.131e-09\t71.525\t100.000\t96.154\t1\t295\t1\t295\t297\t302\t11\t16\t331\t356\t19\t44\t1\t75\t76\t99\t100\t150\t151\t174\t175\t288\t\t\t\t\tT\t1\tTCTGAGCACCGCGAGCAGCCTGGATTAT\t28"""

    def test_parse_empty_output(self, parser):
        """Test parsing empty AIRR output"""
        result = parser.parse_airr_output("")

        assert isinstance(result, AIRRAnalysisResult)
        assert len(result.rearrangements) == 0
        assert result.total_sequences == 0
        assert "error" in result.analysis_metadata

    def test_parse_header_only(self, parser):
        """Test parsing AIRR output with header only"""
        header_only = "sequence_id\tsequence\tv_call\td_call\tj_call"
        result = parser.parse_airr_output(header_only)

        assert isinstance(result, AIRRAnalysisResult)
        assert len(result.rearrangements) == 0
        assert result.total_sequences == 0

    def test_parse_complete_airr_output(self, parser, sample_airr_output):
        """Test parsing complete AIRR output with all fields"""
        result = parser.parse_airr_output(sample_airr_output)

        assert isinstance(result, AIRRAnalysisResult)
        assert len(result.rearrangements) == 1
        assert result.total_sequences == 1
        assert result.productive_sequences == 1

        # Check the rearrangement
        rearrangement = result.rearrangements[0]
        assert isinstance(rearrangement, AIRRRearrangement)
        assert rearrangement.sequence_id == "test_seq"
        assert rearrangement.locus == Locus.IGH
        assert rearrangement.productive == ProductivityStatus.PRODUCTIVE
        assert rearrangement.v_call == "IGHV3-9*01"
        assert rearrangement.d_call == "IGHD1-26*01,IGHD5-5*01,IGHD6-13*01"
        assert rearrangement.j_call == "IGHJ1*01"

        # Check V gene alignment
        assert rearrangement.v_alignment is not None
        assert rearrangement.v_alignment.start == 1
        assert rearrangement.v_alignment.end == 295
        assert rearrangement.v_alignment.identity == 71.525
        assert rearrangement.v_alignment.score == 199.717

        # Check junction region
        assert rearrangement.junction_region is not None
        assert rearrangement.junction_region.junction_length == 28
        assert rearrangement.junction_region.junction_aa == "SSTASSLDY"
        assert (
            rearrangement.junction_region.np2 == "TCTGAGCACCGCGAGCAGCCTGGATTAT"
        )
        assert rearrangement.junction_region.np2_length == 28

        # Check framework regions
        assert rearrangement.fwr1 is not None
        assert rearrangement.fwr1.sequence_aa == "EVQLVESGGGLVQPGRSLRLSCAAS"
        assert rearrangement.fwr1.start == 1
        assert rearrangement.fwr1.end == 75

        # Check CDR regions
        assert rearrangement.cdr1 is not None
        assert rearrangement.cdr1.sequence_aa == "GFTFDDYA"
        assert rearrangement.cdr1.start == 76
        assert rearrangement.cdr1.end == 99

        assert rearrangement.cdr2 is not None
        assert rearrangement.cdr2.sequence_aa == "ITWNSGHI"
        assert rearrangement.cdr2.start == 151
        assert rearrangement.cdr2.end == 174

    def test_parse_productivity_variants(self, parser):
        """Test parsing different productivity status values"""
        test_cases = [
            ("T", ProductivityStatus.PRODUCTIVE),
            ("F", ProductivityStatus.UNPRODUCTIVE),
            ("", ProductivityStatus.UNKNOWN),
            ("TRUE", ProductivityStatus.PRODUCTIVE),
            ("FALSE", ProductivityStatus.UNPRODUCTIVE),
        ]

        for input_val, expected in test_cases:
            header = "sequence_id\tproductive"
            data = f"test\t{input_val}"
            airr_output = f"{header}\n{data}"

            result = parser.parse_airr_output(airr_output)
            assert len(result.rearrangements) == 1
            assert result.rearrangements[0].productive == expected

    def test_parse_locus_variants(self, parser):
        """Test parsing different locus values"""
        test_cases = [
            ("IGH", Locus.IGH),
            ("IGK", Locus.IGK),
            ("IGL", Locus.IGL),
            ("TRA", Locus.TRA),
            ("TRB", Locus.TRB),
            ("igh", Locus.IGH),  # Case insensitive
            ("invalid", None),
        ]

        for input_val, expected in test_cases:
            header = "sequence_id\tlocus"
            data = f"test\t{input_val}"
            airr_output = f"{header}\n{data}"

            result = parser.parse_airr_output(airr_output)
            assert len(result.rearrangements) == 1
            assert result.rearrangements[0].locus == expected

    def test_parse_with_missing_fields(self, parser):
        """Test parsing with some missing fields"""
        header = "sequence_id\tv_call\td_call"
        data = "test\tIGHV3-9*01\t"  # Missing d_call
        airr_output = f"{header}\n{data}"

        result = parser.parse_airr_output(airr_output)
        assert len(result.rearrangements) == 1

        rearrangement = result.rearrangements[0]
        assert rearrangement.sequence_id == "test"
        assert rearrangement.v_call == "IGHV3-9*01"
        assert rearrangement.d_call is None  # Should be None for empty field

    def test_parse_numeric_fields(self, parser):
        """Test parsing of numeric fields with various formats"""
        header = "sequence_id\tv_score\tv_identity\tv_sequence_start\tv_sequence_end"
        data = "test\t199.717\t71.525\t1\t295"
        airr_output = f"{header}\n{data}"

        result = parser.parse_airr_output(airr_output)
        assert len(result.rearrangements) == 1

        rearrangement = result.rearrangements[0]
        assert rearrangement.v_alignment.score == 199.717
        assert rearrangement.v_alignment.identity == 71.525
        assert rearrangement.v_sequence_start == 1
        assert rearrangement.v_sequence_end == 295

    def test_parse_boolean_fields(self, parser):
        """Test parsing of boolean fields"""
        header = "sequence_id\tstop_codon\tvj_in_frame\tcomplete_vdj"
        data = "test\tF\tT\t1"
        airr_output = f"{header}\n{data}"

        result = parser.parse_airr_output(airr_output)
        assert len(result.rearrangements) == 1

        rearrangement = result.rearrangements[0]
        assert rearrangement.stop_codon is False
        assert rearrangement.vj_in_frame is True
        assert rearrangement.complete_vdj is True

    def test_analysis_summary_statistics(self, parser, sample_airr_output):
        """Test that analysis summary statistics are correctly calculated"""
        result = parser.parse_airr_output(sample_airr_output)

        assert result.total_sequences == 1
        assert result.productive_sequences == 1
        assert "IGHV3-9*01" in result.unique_v_genes
        assert "IGHJ1*01" in result.unique_j_genes
        assert len(result.unique_d_genes) >= 3  # Multiple D gene assignments

        # Check that D genes are properly split
        d_genes = result.unique_d_genes
        assert any("IGHD1-26*01" in gene for gene in d_genes)
        assert any("IGHD5-5*01" in gene for gene in d_genes)
        assert any("IGHD6-13*01" in gene for gene in d_genes)

    def test_error_handling_malformed_line(self, parser):
        """Test error handling for malformed data lines"""
        header = "sequence_id\tv_call\td_call\tj_call"
        malformed_data = "test\tIGHV3-9*01"  # Missing fields
        good_data = "test2\tIGHV1-2*01\tIGHD1-1*01\tIGHJ1*01"

        airr_output = f"{header}\n{malformed_data}\n{good_data}"

        result = parser.parse_airr_output(airr_output)

        # Should parse both lines (the parser now handles malformed lines more gracefully)
        assert len(result.rearrangements) == 2
        # Check that both sequence IDs are present
        sequence_ids = [r.sequence_id for r in result.rearrangements]
        assert "test" in sequence_ids
        assert "test2" in sequence_ids
        assert result.analysis_metadata["total_lines_processed"] == 2
        assert result.analysis_metadata["successful_parses"] == 2


class TestAIRRParserIntegration:
    """Integration tests with real IgBLAST output"""

    @pytest.fixture
    def parser(self):
        return AIRRParser()

    def test_real_igblast_output_format(self, parser):
        """Test with realistic IgBLAST AIRR output format"""
        # This is a simplified version of real IgBLAST output
        real_output = """sequence_id	sequence	sequence_aa	locus	stop_codon	vj_in_frame	v_frameshift	productive	rev_comp	complete_vdj	d_frame	v_call	d_call	j_call	v_score	d_score	j_score	v_identity	d_identity	j_identity	v_sequence_start	v_sequence_end	d_sequence_start	d_sequence_end	j_sequence_start	j_sequence_end	junction	junction_length	junction_aa	junction_aa_length	cdr3	cdr3_aa	np1	np1_length	np2	np2_length
humira_seq	GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAATGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGC	EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS	IGH	F		F	T	F	T		IGHV3-9*01	IGHD1-26*01,IGHD5-5*01,IGHD6-13*01	IGHJ1*01	199.717	12.223	44.909	71.525	100.000	96.154	1	295	297	302	331	356	TCTGAGCACCGCGAGCAGCCTGGATTAT	28	SSTASSL DY	9			TCTGAGCACCGCGAGCAGCCTGGATTAT	28"""

        result = parser.parse_airr_output(real_output)

        assert len(result.rearrangements) == 1
        rearrangement = result.rearrangements[0]

        # Verify key fields
        assert rearrangement.sequence_id == "humira_seq"
        assert rearrangement.locus == Locus.IGH
        assert rearrangement.productive == ProductivityStatus.PRODUCTIVE
        assert rearrangement.v_call == "IGHV3-9*01"

        # Verify alignment data
        assert rearrangement.v_alignment.score == 199.717
        assert rearrangement.v_alignment.identity == 71.525
        assert rearrangement.d_alignment.score == 12.223
        assert rearrangement.j_alignment.score == 44.909

        # Verify junction region
        assert (
            rearrangement.junction_region.junction
            == "TCTGAGCACCGCGAGCAGCCTGGATTAT"
        )
        assert rearrangement.junction_region.junction_length == 28
        assert rearrangement.junction_region.junction_aa == "SSTASSL DY"
        # np2 is empty in this test data
        assert rearrangement.junction_region.np2 is None
        assert rearrangement.junction_region.np2_length is None
