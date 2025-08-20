"""
Unit tests for IgBlastAdapterV3 - Simplified User-Selectable Database Approach
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from backend.infrastructure.adapters.igblast_adapter_v3 import IgBlastAdapterV3
from backend.utils.chain_type_utils import ChainTypeUtils
from backend.core.exceptions import ExternalToolError


class TestIgBlastAdapterV3:
    """Test cases for IgBlastAdapterV3."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "builtins.open",
                mock_open(
                    read_data='{"igblast_databases": {"human": {"V": {"name": "Human V", "path": "human/V/test"}}}, "blast_databases": {}}'
                ),
            ):
                with patch.object(
                    IgBlastAdapterV3,
                    "_validate_database_path",
                    return_value=True,
                ):
                    self.adapter = IgBlastAdapterV3()

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        assert self.adapter.tool_name == "igblast"
        assert self.adapter.executable_path == "docker"
        assert isinstance(self.adapter.database_metadata, dict)

    def test_get_available_databases(self):
        """Test getting available databases."""
        databases = self.adapter.get_available_databases()
        assert isinstance(databases, dict)
        assert "human" in databases

    def test_get_blast_databases(self):
        """Test getting BLAST databases."""
        databases = self.adapter.get_blast_databases()
        assert isinstance(databases, dict)

    def test_validate_sequence_nucleotide(self):
        """Test nucleotide sequence validation."""
        # Valid sequence
        self.adapter._validate_sequence("ACGTACGT", "igblastn")

        # Invalid sequence
        with pytest.raises(ValueError, match="Invalid nucleotide sequence"):
            self.adapter._validate_sequence("ACGT123", "igblastn")

    def test_validate_sequence_protein(self):
        """Test protein sequence validation."""
        # Valid sequence
        self.adapter._validate_sequence("QVQLVQS", "igblastp")

        # Invalid sequence
        with pytest.raises(ValueError, match="Invalid protein sequence"):
            self.adapter._validate_sequence("QVQLVQS123", "igblastp")

    def test_validate_sequence_empty(self):
        """Test empty sequence validation."""
        with pytest.raises(ValueError, match="Sequence cannot be empty"):
            self.adapter._validate_sequence("", "igblastn")

    @patch("subprocess.run")
    def test_validate_database_path(self, mock_run):
        """Test database path validation."""
        # Valid database
        mock_run.return_value.returncode = 0
        assert self.adapter._validate_database_path("human/V/test") is True

        # Invalid database
        mock_run.return_value.returncode = 1
        assert self.adapter._validate_database_path("invalid/path") is False

    def test_build_command_basic(self):
        """Test basic command building."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="ACGTACGT",
                v_db="human/V/test",
                blast_type="igblastn",
            )

            assert command[0] == "docker"
            assert command[1] == "exec"
            assert command[2] == "-i"
            assert command[3] == "absequencealign-igblast"
            assert command[4] == "igblastn"
            assert "-query" in command
            assert "/dev/stdin" in command
            assert "-germline_db_V" in command
            assert "human/V/test" in command

    def test_build_command_with_domain_system_imgt(self):
        """Test command building with IMGT domain system."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="QVQLVQS",
                v_db="human/V/test",
                blast_type="igblastp",
                domain_system="imgt",
            )

            assert "-domain_system" in command
            assert "imgt" in command

    def test_build_command_with_domain_system_kabat(self):
        """Test command building with Kabat domain system."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="QVQLVQS",
                v_db="human/V/test",
                blast_type="igblastp",
                domain_system="kabat",
            )

            assert "-domain_system" in command
            assert "kabat" in command

    def test_build_command_invalid_domain_system(self):
        """Test command building with invalid domain system."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            with pytest.raises(ValueError, match="Unsupported domain system"):
                self.adapter._build_command(
                    query_sequence="QVQLVQS",
                    v_db="human/V/test",
                    blast_type="igblastp",
                    domain_system="invalid",
                )

    def test_build_command_domain_system_nucleotide_ignored(self):
        """Test that domain system is ignored for nucleotide IgBLAST."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="ACGTACGT",
                v_db="human/V/test",
                blast_type="igblastn",
                domain_system="imgt",  # Should be ignored for nucleotide
            )

            # Domain system should not be in command for nucleotide
            assert "-domain_system" not in command
            assert "-auxiliary_data" in command

    def test_build_command_with_all_databases(self):
        """Test command building with all databases."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="ACGTACGT",
                v_db="human/V/test",
                d_db="human/D/test",
                j_db="human/J/test",
                c_db="human/C/test",
                blast_type="igblastn",
            )

            assert "-auxiliary_data" in command
            assert "/ncbi-igblast-1.22.0/optional_file/human_gl.aux" in command

    def test_extract_organism_from_db_path(self):
        """Test organism extraction from database path."""
        # Test human
        assert (
            self.adapter._extract_organism_from_db_path(
                "/data/databases/human/V/test"
            )
            == "human"
        )

        # Test mouse
        assert (
            self.adapter._extract_organism_from_db_path(
                "/data/databases/mouse/V/test"
            )
            == "mouse"
        )

        # Test rhesus
        assert (
            self.adapter._extract_organism_from_db_path(
                "/data/databases/rhesus/V/test"
            )
            == "rhesus"
        )

        # Test unknown organism
        assert (
            self.adapter._extract_organism_from_db_path(
                "/data/databases/unknown/V/test"
            )
            is None
        )

        # Test empty path
        assert self.adapter._extract_organism_from_db_path("") is None

    def test_get_auxiliary_data_path(self):
        """Test auxiliary data path generation."""
        # Test human
        assert (
            self.adapter._get_auxiliary_data_path("human")
            == "/ncbi-igblast-1.22.0/optional_file/human_gl.aux"
        )

        # Test mouse
        assert (
            self.adapter._get_auxiliary_data_path("mouse")
            == "/ncbi-igblast-1.22.0/optional_file/mouse_gl.aux"
        )

        # Test rhesus
        assert (
            self.adapter._get_auxiliary_data_path("rhesus")
            == "/ncbi-igblast-1.22.0/optional_file/rhesus_monkey_gl.aux"
        )

        # Test unknown organism
        assert self.adapter._get_auxiliary_data_path("unknown") is None

        # Test empty organism
        assert self.adapter._get_auxiliary_data_path("") is None

    def test_build_command_with_auxiliary_data(self):
        """Test command building includes auxiliary data for human."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="ACGTACGT",
                v_db="/data/databases/human/V/test",
                blast_type="igblastn",
            )

            # Check that auxiliary data is included
            aux_index = command.index("-auxiliary_data")
            aux_path_index = aux_index + 1
            assert (
                command[aux_path_index]
                == "/ncbi-igblast-1.22.0/optional_file/human_gl.aux"
            )

    def test_build_command_without_auxiliary_data(self):
        """Test command building without auxiliary data for unknown organism."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="ACGTACGT",
                v_db="/data/databases/unknown/V/test",
                blast_type="igblastn",
            )

            # Check that auxiliary data is not included
            assert "-auxiliary_data" not in command

            assert "-germline_db_V" in command

    def test_build_command_airr_format(self):
        """Test command building with AIRR format."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="ACGTACGT",
                v_db="human/V/test",
                use_airr_format=True,
            )

            assert "-outfmt" in command
            assert "19" in command  # AIRR format

    def test_build_command_protein(self):
        """Test command building for protein sequences."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            command = self.adapter._build_command(
                query_sequence="QVQLVQS",
                v_db="human/V/test",
                blast_type="igblastp",
            )

            assert command[4] == "igblastp"

    def test_build_command_invalid_v_db(self):
        """Test command building with invalid V database."""
        with patch.object(
            self.adapter, "_validate_database_path", return_value=False
        ):
            with pytest.raises(ValueError, match="Invalid V database path"):
                self.adapter._build_command(
                    query_sequence="ACGTACGT", v_db="invalid/path"
                )

    @patch("subprocess.Popen")
    def test_execute_success(self, mock_popen):
        """Test successful execution."""
        # Mock successful subprocess execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (
            "# Query: test\nV\tquery\tIGHV1-2*01\t100.0\t300\t0\t0\t1\t300\t1\t300\t0.0\t600",
            "",
        )
        mock_popen.return_value = mock_process

        with patch.object(
            self.adapter, "_validate_database_path", return_value=True
        ):
            result = self.adapter.execute(
                query_sequence="ACGTACGT", v_db="human/V/test"
            )

            assert result["blast_type"] == "igblastn"
            assert "hits" in result
            assert "databases_used" in result
            assert result["databases_used"]["V"] == "human/V/test"

    @patch("subprocess.Popen")
    def test_execute_failure(self, mock_popen):
        """Test execution failure."""
        # Mock failed subprocess execution
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = ("", "Error: Invalid database")
        mock_popen.return_value = mock_process

        with pytest.raises(ExternalToolError):
            self.adapter.execute(
                query_sequence="ACGTACGT", v_db="human/V/test"
            )

    def test_parse_tabular_output_empty(self):
        """Test parsing empty tabular output."""
        result = self.adapter.tabular_parser.parse("", "igblastn")

        assert result["blast_type"] == "igblastn"
        assert result["hits"] == []
        assert result["total_hits"] == 0

    def test_parse_tabular_output_valid(self):
        """Test parsing valid tabular output."""
        output = """# Query: test
# Database: test_db
V query IGHV1-2*01 100.0 300 0 0 0 1 300 1 300 0.0 600
V-(D)-J rearrangement summary
IGHV1-2*01 N/A IGHJ1*01 IGH No In Yes +
"""

        result = self.adapter.tabular_parser.parse(output, "igblastn")

        assert result["blast_type"] == "igblastn"
        assert len(result["hits"]) == 1
        assert result["hits"][0]["hit_type"] == "V"
        assert result["hits"][0]["v_gene"] == "IGHV1-2*01"
        assert result["analysis_summary"]["v_gene"] == "IGHV1-2*01"
        assert result["analysis_summary"]["chain_type"] == "IGH"

    def test_parse_airr_output_empty(self):
        """Test parsing empty AIRR output."""
        result = self.adapter.airr_parser.parse("", "igblastn")

        assert result["blast_type"] == "igblastn"
        assert result["hits"] == []
        assert result["total_hits"] == 0

    def test_parse_airr_output_valid(self):
        """Test parsing valid AIRR output."""
        output = """sequence_id\tsequence\tsequence_aa\tlocus\tstop_codon\tvj_in_frame\tv_frameshift\tproductive\trev_comp\tcomplete_vdj\td_frame\tv_call\td_call\tj_call
query\tACGTACGT\tQVQLVQS\tIGH\tF\tT\tF\tT\tF\tF\tF\tIGHV1-2*01\tN/A\tIGHJ1*01"""

        result = self.adapter.airr_parser.parse(output, "igblastn")

        assert result["blast_type"] == "igblastn"
        assert len(result["hits"]) == 1
        assert result["hits"][0]["v_call"] == "IGHV1-2*01"
        assert result["analysis_summary"]["v_gene"] == "IGHV1-2*01"
        assert result["analysis_summary"]["productive"] == "T"

    def test_extract_chain_type(self):
        """Test chain type extraction."""
        assert ChainTypeUtils.extract_chain_type("IGHV1-2*01") == "IGH"
        assert ChainTypeUtils.extract_chain_type("IGKV1-2*01") == "IGK"
        assert ChainTypeUtils.extract_chain_type("IGLV1-2*01") == "IGL"
        assert ChainTypeUtils.extract_chain_type("TRAV1-2*01") == "TCR"
        assert ChainTypeUtils.extract_chain_type("UNKNOWN") == "unknown"

    def test_get_subject_url(self):
        """Test subject URL generation."""
        # IMGT URLs
        url = self.adapter._get_subject_url("IGHV1-2*01")
        assert "imgt.org" in url
        assert "IGHV1-2*01" in url

        # Empty/NA cases
        assert self.adapter._get_subject_url("") == ""
        assert self.adapter._get_subject_url("N/A") == ""

        # Unknown gene
        assert self.adapter._get_subject_url("UNKNOWN") == ""

    def test_get_timeout(self):
        """Test timeout configuration."""
        assert self.adapter._get_timeout() == 300  # 5 minutes
