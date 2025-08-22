"""
Unit tests for IgBLAST adapter V2 with advanced features.
Tests smart chain type detection, AIRR format support, and enhanced functionality.
"""

import os
from unittest.mock import Mock, patch

import pytest

from backend.core.exceptions import ExternalToolError
from backend.infrastructure.adapters.igblast_adapter_v2 import IgBlastAdapterV2
from backend.utils.chain_type_utils import ChainTypeUtils


@pytest.mark.skipif(
    os.getenv("CI", "false").lower() == "true",
    reason="Skip IgBLAST adapter tests in CI environment - requires Docker containers",
)
class TestIgBlastAdapterV2:
    """Test suite for IgBLAST adapter V2 with advanced features."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.object(
            IgBlastAdapterV2,
            "_validate_tool_installation",
            return_value=None,
        ):
            self.adapter = IgBlastAdapterV2()
        self.test_sequence = "GAAGTGCAGCTGGTGGAAAGCGGCGGCGGCCTGGTGCAGCCGGGCCGCAGCCTGCGCCTGAGCTGCGCGGCGAGCGGCTTTACCTTTGATGATTATGCGATGCATTGGGTGCGCCAGGCGCCGGGCAAAGGCCTGGAGTGGGTGAGCGCGATTACCTGGAACAGCGGCCATATTGATTATGCGGATAGCGTGGAAGGCCGCTTTACCATTAGCCGCGATAACGCGAAAAACAGCCTGTATCTGCAGATGAACAGCCTGCGCGCGGAAGATACCGCGGTGTATTATTGCGCGAAAGTGAGCTATCTGAGCACCGCGAGCAGCCTGGATTATTGGGGCCAGGGCACCCTGGTGACCGTGAGCAGCGCGAGCACCAAAGGCCCGAGCGTGTTTCCGCTGGCGCCGAGCAGCAAAAGCACCAGCGGCGGCACCGCGGCGCTGGGCTGCCTGGTGAAAGATTATTTTCCGGAACCGGTGACCGTGAGCTGGAACAGCGCGCGCTGACCAGCGGCGTGCATACCTTTCCGGCGGTGCTGCAGAGCAGCGGCCTGTATAGCCTGAGCAGCGTGGTGACCGTGCCGAGCAGCAGCCTGGGCACCCAGACCTATATTTGCAACGTGAACCATAAACCGAGCAACACCAAAGTGGATAAAAAAGTGGAACCGAAAAGCTGCGATAAAACCCATACCTGCCCGCCGTGCCCGGCGCCGGAACTGCTGGGCGGCCCGAGCGTGTTTCTGTTTCCGCCGAAACCGAAAGATACCCTGATGATTAGCCGCACCCCGGAAGTGACCTGCGTGGTGGTGGATGTGAGCCATGAAGATCCGGAAGTGAAATTTAACTGGTATGTGGATGGTGTGGAAGTGCATAACGCGAAAACCAAACCGCGCGAAGAACAGTATAACAGCACCTATCGCGTGGTGAGCGTGCTGACCGTGCTGCATCAGGATTGGCTGAACGGCAAAGAATATAAATGCAAAGTGAGCAACAAAGCGCTGCCGGCGCCGATTGAAAAAACCATTAGCAAAGCGAAGGCCAGCCGCGCGAACCGCAGGTGTATACCCTGCCGCCGAGCCGCGATGAACTGACCAAAAACCAGGTGAGCCTGACCTGCCTGGTGAAAGGCTTTTATCCGAGCGATATTGCGGTGGAATGGGAAAGCAACGGCCAGCCGGAAAACAACTATAAAACCACCCCGCCGGTGCTGGATAGCGATGGCAGCTTTTTTCTGTATAGCAAACTGACCGTGGATAAAAGCCGCTGGCAGCAGGGCAACGTGTTTAGCTGCAGCGTGATGCATGAAGCGCTGCATAACCATTATACCCAGAAAAGCCTGAGCCTGAGCCCGGGCAAA"

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        assert self.adapter.tool_name == "igblast"
        assert self.adapter.executable_path == "docker"
        assert "igblastn" in self.adapter._supported_blast_types
        assert "igblastp" in self.adapter._supported_blast_types

    def test_supported_organisms_discovery(self):
        """Test supported organisms discovery."""
        organisms = self.adapter._discover_supported_organisms()
        assert isinstance(organisms, list)
        assert len(organisms) > 0
        assert "human" in organisms
        assert "mouse" in organisms

    def test_validate_sequence_nucleotide(self):
        """Test nucleotide sequence validation."""
        # Valid nucleotide sequence
        self.adapter._validate_sequence("ACGTN", "igblastn")

        # Invalid nucleotide sequence
        with pytest.raises(ValueError, match="Invalid nucleotide sequence"):
            self.adapter._validate_sequence("ACGTX", "igblastn")

    def test_validate_sequence_protein(self):
        """Test protein sequence validation."""
        # Valid protein sequence
        self.adapter._validate_sequence("ACDEFGHIKLMNPQRSTVWY", "igblastp")

        # Invalid protein sequence
        with pytest.raises(ValueError, match="Invalid protein sequence"):
            self.adapter._validate_sequence(
                "ACDEFGHIKLMNPQRSTVWYX", "igblastp"
            )

    def test_detect_chain_type_heavy(self):
        """Test chain type detection for heavy chain."""
        mock_output = "V\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200"

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = (mock_output, "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            chain_type = self.adapter._detect_chain_type(
                self.test_sequence, "human"
            )
            assert chain_type == "IGH"

    def test_detect_chain_type_light(self):
        """Test chain type detection for light chain."""
        mock_output = "V\tquery\tIGKV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200"

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = (mock_output, "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            chain_type = self.adapter._detect_chain_type(
                self.test_sequence, "human"
            )
            assert chain_type == "IGK"

    def test_detect_chain_type_tcr(self):
        """Test chain type detection for TCR."""
        mock_output = "V\tquery\tTRBV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200"

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = (mock_output, "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            chain_type = self.adapter._detect_chain_type(
                self.test_sequence, "human"
            )
            assert chain_type == "TCR"

    def test_detect_chain_type_unknown(self):
        """Test chain type detection for unknown gene."""
        mock_output = "V\tquery\tUNKNOWN-1*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200"

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = (mock_output, "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            chain_type = self.adapter._detect_chain_type(
                self.test_sequence, "human"
            )
            assert chain_type == "unknown"

    def test_detect_chain_type_failure(self):
        """Test chain type detection failure handling."""
        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = ("", "Error")
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            chain_type = self.adapter._detect_chain_type(
                self.test_sequence, "human"
            )
            assert chain_type == "unknown"

    def test_build_command_nucleotide(self):
        """Test command building for nucleotide search."""
        command = self.adapter._build_command(
            query_sequence=self.test_sequence,
            organism="mouse",
            blast_type="igblastn",
        )

        assert command[0] == "docker"
        assert command[1] == "exec"
        assert command[2] == "absequencealign-igblast"
        assert command[3] == "igblastn"
        assert "-query" in command
        assert "/dev/stdin" in command
        assert "-organism" in command
        assert "mouse" in command
        assert "-outfmt" in command
        assert "7" in command

    def test_build_command_protein(self):
        """Test command building for protein search."""
        command = self.adapter._build_command(
            query_sequence="QVQLVQSGAEVKKPGASVKVSCKASGYTFTDYYMHWVRQAPGQGLEWMG",
            organism="human",
            blast_type="igblastp",
        )

        assert command[0] == "docker"
        assert command[1] == "exec"
        assert command[2] == "absequencealign-igblast"
        assert command[3] == "igblastp"
        assert "-query" in command
        assert "/dev/stdin" in command
        assert "-organism" in command
        assert "human" in command
        assert "-outfmt" in command
        assert "7" in command

    def test_build_command_airr_format(self):
        """Test command building with AIRR format."""
        command = self.adapter._build_command(
            query_sequence=self.test_sequence,
            organism="human",
            blast_type="igblastn",
            use_airr_format=True,
        )

        assert "-outfmt" in command
        assert "19" in command  # AIRR format

    def test_build_command_missing_sequence(self):
        """Test command building with missing sequence."""
        with pytest.raises(ValueError, match="query_sequence is required"):
            self.adapter._build_command(
                organism="mouse", blast_type="igblastn"
            )

    def test_build_command_invalid_blast_type(self):
        """Test command building with invalid blast type."""
        with pytest.raises(ValueError, match="Unsupported IgBLAST type"):
            self.adapter._build_command(
                query_sequence=self.test_sequence,
                organism="mouse",
                blast_type="invalid_blast_type",
            )

    def test_build_command_invalid_organism(self):
        """Test command building with invalid organism."""
        with pytest.raises(ValueError, match="Unsupported organism"):
            self.adapter._build_command(
                query_sequence=self.test_sequence,
                organism="invalid_organism",
                blast_type="igblastn",
            )

    @patch("subprocess.Popen")
    def test_execute_success(self, mock_popen):
        """Test successful execution."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            "# IGBLASTN 1.22.0\n# Query: query\n# V-(D)-J rearrangement summary\nIGHV1-2*01\tIGHD2-2*01\tIGHJ2*01\tIGH\tNo\tIn-frame\tYes\t+\tNo",
            "",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = self.adapter.execute(
            query_sequence=self.test_sequence,
            organism="mouse",
            blast_type="igblastn",
        )

        assert result["blast_type"] == "igblastn"
        assert "hits" in result
        assert "total_hits" in result

    @patch("subprocess.Popen")
    def test_execute_failure(self, mock_popen):
        """Test execution failure."""
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "Error")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        with pytest.raises(ExternalToolError):
            self.adapter.execute(
                query_sequence=self.test_sequence,
                organism="mouse",
                blast_type="igblastn",
            )

    @patch("subprocess.Popen")
    def test_execute_with_chain_detection(self, mock_popen):
        """Test execution with chain type detection enabled."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            "# IGBLASTN 1.22.0\n# Query: query\nV\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200",
            "",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = self.adapter.execute(
            query_sequence=self.test_sequence,
            organism="mouse",
            blast_type="igblastn",
            enable_chain_detection=True,
        )

        assert "detected_chain_type" in result
        assert result["detected_chain_type"] == "IGH"

    @patch("subprocess.Popen")
    def test_execute_with_airr_format(self, mock_popen):
        """Test execution with AIRR format."""
        mock_process = Mock()
        mock_process.communicate.return_value = (
            '{"v_call": "IGHV1-2*01", "d_call": "IGHD2-2*01", "j_call": "IGHJ2*01", "locus": "IGH", "productive": "T", "cdr3": "ACGTACGT"}',
            "",
        )
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        result = self.adapter.execute(
            query_sequence=self.test_sequence,
            organism="human",
            blast_type="igblastn",
            use_airr_format=True,
        )

        assert result["blast_type"] == "igblastn"
        assert "airr_data" in result
        assert result["airr_data"]["v_call"] == "IGHV1-2*01"

    def test_parse_tabular_output_empty(self):
        """Test parsing empty tabular output."""
        result = self.adapter._parse_tabular_output("", "igblastn")
        assert result["blast_type"] == "igblastn"
        assert result["total_hits"] == 0
        assert result["hits"] == []

    def test_parse_tabular_output_valid(self):
        """Test parsing valid tabular output."""
        output = """# IGBLASTN 1.22.0
# Query: query
# Database: /data/internal_data/mouse/mouse_V
V\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200
D\tquery\tIGHD2-2*01\t100.0\t6\t0\t0\t0\t297\t302\t11\t16\t116\t12.2
J\tquery\tIGHJ2*01\t96.2\t26\t1\t0\t0\t331\t356\t19\t44\t2.99e-08\t44.9
# V-(D)-J rearrangement summary
IGHV1-2*01\tIGHD2-2*01\tIGHJ2*01\tIGH\tNo\tIn-frame\tYes\t+\tNo
# V-(D)-J junction details
GAAAG\tT\tGAGCTA\tTCTGAGCACCGCGAGCAGCCTGGATTAT\tTGGGG"""

        result = self.adapter._parse_tabular_output(output, "igblastn")

        assert result["blast_type"] == "igblastn"
        assert result["total_hits"] == 3
        assert len(result["hits"]) == 3

        # Check V gene hit
        v_hit = result["hits"][0]
        assert v_hit["hit_type"] == "V"
        assert v_hit["v_gene"] == "IGHV1-2*01"
        assert v_hit["chain_type"] == "IGH"

        # Check analysis summary
        summary = result["analysis_summary"]
        assert summary["v_gene"] == "IGHV1-2*01"
        assert summary["d_gene"] == "IGHD2-2*01"
        assert summary["j_gene"] == "IGHJ2*01"
        assert summary["chain_type"] == "IGH"  # From rearrangement summary
        assert summary["productive"] == "Yes"
        assert summary["stop_codon"] == "No"

    def test_parse_tabular_output_no_cdr3(self):
        """Test parsing tabular output without CDR3."""
        output = """# IGBLASTN 1.22.0
# Query: query
V\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200
# V-(D)-J rearrangement summary
IGHV1-2*01\tN/A\tIGHJ2*01\tIGH\tNo\tIn-frame\tYes\t+\tNo"""

        result = self.adapter._parse_tabular_output(output, "igblastn")

        assert result["total_hits"] == 1
        assert result["analysis_summary"]["d_gene"] is None

    def test_parse_tabular_output_multiple_hits(self):
        """Test parsing tabular output with multiple hits."""
        output = """# IGBLASTN 1.22.0
# Query: query
V\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200
V\tquery\tIGHV1-3*01\t94.0\t300\t18\t0\t0\t1\t300\t1\t300\t1e-48\t195
D\tquery\tIGHD2-2*01\t100.0\t6\t0\t0\t0\t297\t302\t11\t16\t116\t12.2
J\tquery\tIGHJ2*01\t96.2\t26\t1\t0\t0\t331\t356\t19\t44\t2.99e-08\t44.9"""

        result = self.adapter._parse_tabular_output(output, "igblastn")

        assert result["total_hits"] == 4
        assert len([h for h in result["hits"] if h["hit_type"] == "V"]) == 2

    def test_parse_tabular_output_light_chain(self):
        """Test parsing tabular output for light chain."""
        output = """# IGBLASTN 1.22.0
# Query: query
V\tquery\tIGKV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200
J\tquery\tIGKJ2*01\t96.2\t26\t1\t0\t0\t331\t356\t19\t44\t2.99e-08\t44.9
# V-(D)-J rearrangement summary
IGKV1-2*01\tN/A\tIGKJ2*01\tIGK\tNo\tIn-frame\tYes\t+\tNo"""

        result = self.adapter._parse_tabular_output(output, "igblastn")

        assert result["total_hits"] == 2
        v_hit = result["hits"][0]
        assert v_hit["v_gene"] == "IGKV1-2*01"
        assert v_hit["chain_type"] == "IGK"

    def test_parse_tabular_output_unproductive(self):
        """Test parsing tabular output for unproductive sequence."""
        output = """# IGBLASTN 1.22.0
# Query: query
V\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200
# V-(D)-J rearrangement summary
IGHV1-2*01\tN/A\tIGHJ2*01\tIGH\tYes\tOut-of-frame\tNo\t+\tNo"""

        result = self.adapter._parse_tabular_output(output, "igblastn")

        summary = result["analysis_summary"]
        assert summary["stop_codon"] == "Yes"
        assert summary["productive"] == "No"

    def test_parse_tabular_output_protein(self):
        """Test parsing tabular output for protein search."""
        output = """# IGBLASTP 1.22.0
# Query: query
V\tquery\tIGHV1-2*01\t95.0\t300\t15\t0\t0\t1\t300\t1\t300\t1e-50\t200"""

        result = self.adapter._parse_tabular_output(output, "igblastp")

        assert result["blast_type"] == "igblastp"
        assert result["total_hits"] == 1

    def test_parse_airr_output_empty(self):
        """Test parsing empty AIRR output."""
        result = self.adapter._parse_airr_output("", "igblastn")
        assert result["blast_type"] == "igblastn"
        assert result["total_hits"] == 0
        assert result["hits"] == []

    def test_parse_airr_output_valid(self):
        """Test parsing valid AIRR output."""
        output = """{"v_call": "IGHV1-2*01", "d_call": "IGHD2-2*01", "j_call": "IGHJ2*01", "locus": "IGH", "productive": "T", "cdr3": "ACGTACGT", "cdr3_start": 100, "cdr3_end": 108, "v_identity": 95.0, "j_identity": 96.2, "d_identity": 100.0}"""

        result = self.adapter._parse_airr_output(output, "igblastn")

        assert result["blast_type"] == "igblastn"
        assert result["total_hits"] == 1
        assert "airr_data" in result

        hit = result["hits"][0]
        assert hit["v_gene"] == "IGHV1-2*01"
        assert hit["d_gene"] == "IGHD2-2*01"
        assert hit["j_gene"] == "IGHJ2*01"
        assert hit["chain_type"] == "IGH"
        assert hit["productive"] == "T"
        assert hit["cdr3_sequence"] == "ACGTACGT"
        assert hit["cdr3_start"] == 100
        assert hit["cdr3_end"] == 108
        assert hit["v_identity"] == 95.0
        assert hit["j_identity"] == 96.2
        assert hit["d_identity"] == 100.0

    def test_parse_airr_output_invalid_json(self):
        """Test parsing AIRR output with invalid JSON."""
        output = "invalid json content"

        result = self.adapter._parse_airr_output(output, "igblastn")

        assert result["total_hits"] == 0
        assert result["hits"] == []

    def test_extract_chain_type(self):
        """Test chain type extraction from gene names."""
        assert ChainTypeUtils.extract_chain_type("IGHV1-2*01") == "IGH"
        assert ChainTypeUtils.extract_chain_type("IGKV1-2*01") == "IGK"
        assert ChainTypeUtils.extract_chain_type("IGLV1-2*01") == "IGL"
        assert ChainTypeUtils.extract_chain_type("TRBV1-2*01") == "TCR"
        assert ChainTypeUtils.extract_chain_type("TRAV1-2*01") == "TCR"
        assert ChainTypeUtils.extract_chain_type("UNKNOWN") == "unknown"

    def test_get_subject_url_imgt(self):
        """Test IMGT URL generation for Ig genes."""
        url = self.adapter._get_subject_url("IGHV1-2*01")
        assert "imgt.org" in url
        assert "IGHV1-2*01" in url

    def test_get_subject_url_tcr(self):
        """Test IMGT URL generation for TCR genes."""
        url = self.adapter._get_subject_url("TRBV1-2*01")
        assert "imgt.org" in url
        assert "TRBV1-2*01" in url

    def test_get_subject_url_unknown(self):
        """Test URL generation for unknown genes."""
        url = self.adapter._get_subject_url("UNKNOWN")
        assert url == ""

    def test_get_subject_url_empty(self):
        """Test URL generation for empty gene name."""
        url = self.adapter._get_subject_url("")
        assert url == ""

    def test_get_subject_url_none(self):
        """Test URL generation for None gene name."""
        url = self.adapter._get_subject_url(None)
        assert url == ""

    def test_get_subject_url_na(self):
        """Test URL generation for N/A gene name."""
        url = self.adapter._get_subject_url("N/A")
        assert url == ""


if __name__ == "__main__":
    pytest.main([__file__])
