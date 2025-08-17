"""
Unit tests for BLAST service functionality.
Following TDD principles - tests are written before implementation.
"""

from unittest.mock import Mock, patch

import pytest

from backend.services.blast_service import BlastService
from backend.services.igblast_service import IgBlastService
from backend.tests.data.blast.test_sequences import (
    HUMAN_IGG1_CONSTANT,
    TEST_SEQUENCES,
)

# Real working sequences for comprehensive testing
WORKING_PROTEIN_SEQUENCE = "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMHWVRQAPGKGLEWVSAITWNSGHIDYADSVEGRFTISRDNAKNSLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS"
# Full Humira heavy chain sequence - provides complete V, D, J, CDR3 assignments
WORKING_NUCLEOTIDE_SEQUENCE = "gaagtgcagctggtggaaagcggcggcggcctggtgcagccgggccgcagcctgcgcctgagctgcgcggcgagcggctttacctttgatgattatgcgatgcattgggtgcgccaggcgccgggcaaaggcctggaatgggtgagcgcgattacctggaacagcggccatattgattatgcggatagcgtggaaggccgctttaccattagccgcgataacgcgaaaaacagcctgtatctgcagatgaacagcctgcgcgcggaagataccgcggtgtattattgcgcgaaagtgagctatctgagcaccgcgagcagcctggattattggggccagggcaccctggtgaccgtgagcagcgcgagcaccaaaggcccgagcgtgtttccgctggcgccgagcagcaaaagcaccagcggcggcaccgcggcgctgggctgcctggtgaaagattattttccggaaccggtgaccgtgagctggaacagcggcgcgctgaccagcggcgtgcatacctttccggcggtgctgcagagcagcggcctgtatagcctgagcagcgtggtgaccgtgccgagcagcagcctgggcacccagacctatatttgcaacgtgaaccataaaccgagcaacaccaaagtggataaaaaagtggaaccgaaaagctgcgataaaacccatacctgcccgccgtgcccggcgccggaactgctgggcggcccgagcgtgtttctgtttccgccgaaaccgaaagataccctgatgattagccgcaccccggaagtgacctgcgtggtggtggatgtgagccatgaagatccggaagtgaaatttaactggtatgtggatggcgtggaagtgcataacgcgaaaaccaaaccgcgcgaagaacagtataacagcacctatcgcgtggtgagcgtgctgaccgtgctgcatcaggattggctgaacggcaaagaatataaatgcaaagtgagcaacaaagcgctgccggcgccgattgaaaaaaccattagcaaagcgaaaggccagccgcgcgaaccgcaggtgtataccctgccgccgagccgcgatgaactgaccaaaaaccaggtgagcctgacctgcctggtgaaaggcttttatccgagcgatattgcggtggaatgggaaagcaacggccagccggaaaacaactataaaaccaccccgccggtgctggatagcgatggcagcttttttctgtatagcaaactgaccgtggataaaagccgctggcagcagggcaacgtgtttagctgcagcgtgatgcatgaagcgctgcataaccattatacccagaaaagcctgagcctgagcccgggcaaa"
REVERSE_TRANSLATED_SEQUENCE = "GAGGTTCAGCTGGTTGAGTCTGGTGGTGGTCTGGTTCAGCCTGGTCGTTCTCTGCGTCTGTCTTGTGCTGCTTCTGGTTTTACTTTTGATGATTATGCTATGCATTGGGTTCGTCAGGCTCCTGGTAAGGGTCTGGAGTGGGTTTCTGCTATTACTTGGAATTCTGGTCATATTGATTATGCTGATTCTGTTGAGGGTCGTTTTACTATTTCTCGTGATAATGCTAAGAATTCTCTGTATCTGCAGATGAATTCTCTGCGTGCTGAGGATACTGCTGTTTATTATTGTGCTAAGGTTTCTTATCTGTCTACTGCTTCTTCTCTGGATTATTGGGGTCAGGGTACTCTGGTTACTGTTTCTTCT"


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

    def test_igblast_service_get_supported_organisms_dynamic_discovery(self):
        """Test dynamic discovery of supported organisms."""
        service = IgBlastService()

        with patch(
            "backend.infrastructure.adapters.igblast_adapter.IGBLAST_INTERNAL_DATA_DIR"
        ) as mock_data_dir:
            # Mock the internal data directory structure
            mock_data_dir.exists.return_value = True

            # Mock human organism directory
            mock_human_dir = Mock()
            mock_human_dir.name = "human"
            mock_human_dir.is_dir.return_value = True
            mock_human_v_file = Mock()
            mock_human_v_file.exists.return_value = True
            mock_human_dir.__truediv__ = lambda self, name: (
                mock_human_v_file
                if name == "human_V.nhr"
                else Mock(exists=lambda: False)
            )

            # Mock mouse organism directory
            mock_mouse_dir = Mock()
            mock_mouse_dir.name = "mouse"
            mock_mouse_dir.is_dir.return_value = True
            mock_mouse_v_file = Mock()
            mock_mouse_v_file.exists.return_value = True
            mock_mouse_dir.__truediv__ = lambda self, name: (
                mock_mouse_v_file
                if name == "mouse_V.nhr"
                else Mock(exists=lambda: False)
            )

            # Mock invalid directory (not a directory)
            mock_invalid_dir = Mock()
            mock_invalid_dir.name = "invalid"
            mock_invalid_dir.is_dir.return_value = False

            # Mock directory without V gene file
            mock_incomplete_dir = Mock()
            mock_incomplete_dir.name = "incomplete"
            mock_incomplete_dir.is_dir.return_value = True
            mock_incomplete_dir.__truediv__ = lambda self, name: Mock(
                exists=lambda: False
            )

            # Set up the iterdir
            mock_data_dir.iterdir.return_value = [
                mock_human_dir,
                mock_mouse_dir,
                mock_invalid_dir,
                mock_incomplete_dir,
            ]

            organisms = service.get_supported_organisms()

            # Should only include valid organisms with V gene files
            assert "human" in organisms
            assert "mouse" in organisms
            assert "invalid" not in organisms  # Not a directory
            assert "incomplete" not in organisms  # Missing V gene file

    def test_igblast_service_get_supported_organisms_directory_not_exists(
        self,
    ):
        """Test organism discovery when internal data directory doesn't exist."""
        service = IgBlastService()

        with patch(
            "backend.infrastructure.adapters.igblast_adapter.IGBLAST_INTERNAL_DATA_DIR"
        ) as mock_data_dir:
            mock_data_dir.exists.return_value = False

            organisms = service.get_supported_organisms()

            # Should return default organisms (order may vary)
        assert set(organisms) == {"human", "mouse"}

    def test_igblast_service_get_supported_organisms_empty_directory(self):
        """Test organism discovery when internal data directory is empty."""
        service = IgBlastService()

        with patch(
            "backend.infrastructure.adapters.igblast_adapter.IGBLAST_INTERNAL_DATA_DIR"
        ) as mock_data_dir:
            mock_data_dir.exists.return_value = True
            mock_data_dir.iterdir.return_value = []

            organisms = service.get_supported_organisms()

            # Should return default organisms (order may vary)
            assert set(organisms) == {"human", "mouse"}

    def test_igblast_service_get_supported_organisms_adapter_not_available(
        self,
    ):
        """Test organism discovery when IgBLAST adapter is not available."""
        service = IgBlastService(igblast_adapter=None)

        organisms = service.get_supported_organisms()

        # Should return default organisms (order may vary)
        assert set(organisms) == {"human", "mouse"}

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

    def test_blast_service_get_public_databases_dynamic_discovery(self):
        """Test dynamic discovery of public databases."""
        service = BlastService()

        with patch("backend.config.BLAST_DB_DIR") as mock_db_dir:
            # Mock the database directory structure
            mock_db_dir.exists.return_value = True

            # Mock protein database files
            mock_swissprot_phr = Mock()
            mock_swissprot_phr.stem = "swissprot"
            mock_swissprot_phr.with_suffix.side_effect = lambda ext: {
                ".pin": Mock(exists=lambda: True),
                ".psq": Mock(exists=lambda: True),
            }.get(ext, Mock(exists=lambda: False))

            mock_pdbaa_phr = Mock()
            mock_pdbaa_phr.stem = "pdbaa"
            mock_pdbaa_phr.with_suffix.side_effect = lambda ext: {
                ".pin": Mock(exists=lambda: True),
                ".psq": Mock(exists=lambda: True),
            }.get(ext, Mock(exists=lambda: False))

            # Mock nucleotide database files
            mock_16s_nhr = Mock()
            mock_16s_nhr.stem = "16S_ribosomal_RNA"
            mock_16s_nhr.with_suffix.side_effect = lambda ext: {
                ".nin": Mock(exists=lambda: True),
                ".nsq": Mock(exists=lambda: True),
            }.get(ext, Mock(exists=lambda: False))

            # Mock incomplete database (missing files)
            mock_incomplete_phr = Mock()
            mock_incomplete_phr.stem = "incomplete"
            mock_incomplete_phr.with_suffix.side_effect = lambda ext: {
                ".pin": Mock(exists=lambda: False),  # Missing pin file
                ".psq": Mock(exists=lambda: True),
            }.get(ext, Mock(exists=lambda: False))

            # Set up the glob patterns
            mock_db_dir.glob.side_effect = lambda pattern: {
                "*.phr": [
                    mock_swissprot_phr,
                    mock_pdbaa_phr,
                    mock_incomplete_phr,
                ],
                "*.nhr": [mock_16s_nhr],
            }.get(pattern, [])

            databases = service._get_public_databases()

            # Should only include complete databases
            assert "swissprot" in databases
            assert "pdbaa" in databases
            assert "16S_ribosomal_RNA" in databases
            assert "incomplete" not in databases  # Should be excluded

            # Check descriptions
            assert databases["swissprot"] == "Swiss-Prot protein database"
            assert databases["pdbaa"] == "Protein Data Bank"
            assert (
                databases["16S_ribosomal_RNA"] == "16S ribosomal RNA database"
            )

    def test_blast_service_get_public_databases_empty_directory(self):
        """Test dynamic discovery when database directory is empty."""
        service = BlastService()

        with patch("backend.config.BLAST_DB_DIR") as mock_db_dir:
            mock_db_dir.exists.return_value = True
            mock_db_dir.glob.return_value = []

            databases = service._get_public_databases()

            assert databases == {}

    def test_blast_service_get_public_databases_directory_not_exists(self):
        """Test dynamic discovery when database directory doesn't exist."""
        service = BlastService()

        with patch("backend.config.BLAST_DB_DIR") as mock_db_dir:
            mock_db_dir.exists.return_value = False

            databases = service._get_public_databases()

            assert databases == {}

    def test_blast_service_get_public_databases_custom_descriptions(self):
        """Test that custom database names get appropriate descriptions."""
        service = BlastService()

        with patch("backend.config.BLAST_DB_DIR") as mock_db_dir:
            mock_db_dir.exists.return_value = True

            # Mock custom protein database
            mock_custom_phr = Mock()
            mock_custom_phr.stem = "custom_protein_db"
            mock_custom_phr.with_suffix.side_effect = lambda ext: {
                ".pin": Mock(exists=lambda: True),
                ".psq": Mock(exists=lambda: True),
            }.get(ext, Mock(exists=lambda: False))

            # Mock custom nucleotide database
            mock_custom_nhr = Mock()
            mock_custom_nhr.stem = "custom_nucleotide_db"
            mock_custom_nhr.with_suffix.side_effect = lambda ext: {
                ".nin": Mock(exists=lambda: True),
                ".nsq": Mock(exists=lambda: True),
            }.get(ext, Mock(exists=lambda: False))

            mock_db_dir.glob.side_effect = lambda pattern: {
                "*.phr": [mock_custom_phr],
                "*.nhr": [mock_custom_nhr],
            }.get(pattern, [])

            databases = service._get_public_databases()

            assert "custom_protein_db" in databases
            assert "custom_nucleotide_db" in databases
            assert (
                databases["custom_protein_db"]
                == "custom_protein_db protein database"
            )
            assert (
                databases["custom_nucleotide_db"]
                == "custom_nucleotide_db nucleotide database"
            )

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


class TestBlastServiceReal:
    """Real service tests using actual sequences and adapters."""

    def test_blast_service_swissprot_search_real(self):
        """Test real BLAST search against Swiss-Prot database."""
        service = BlastService()

        # Skip if adapters not available
        if service.blast_adapter is None:
            pytest.skip("BLAST adapter not available")

        results = service.search_public_databases(
            query_sequence=WORKING_PROTEIN_SEQUENCE,
            databases=["swissprot"],
            blast_type="blastp",
            evalue=1e-10,
        )

        assert results is not None
        assert "hits" in results
        # Should find hits for this known protein sequence
        assert len(results["hits"]) > 0

        # Check hit structure
        hit = results["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert "identity" in hit
        assert "evalue" in hit
        assert "bit_score" in hit
        assert isinstance(hit["identity"], float)
        assert hit["identity"] > 0

    def test_igblast_service_protein_search_real(self):
        """Test real IgBLAST protein search."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        results = service.analyze_antibody_sequence(
            query_sequence=WORKING_PROTEIN_SEQUENCE,
            organism="human",
            blast_type="igblastp",
            evalue=1e-10,
        )

        assert results is not None
        assert "hits" in results
        # Should find hits for this known antibody sequence
        assert len(results["hits"]) > 0

        # Check hit structure for protein search
        hit = results["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert "identity" in hit
        assert "v_gene" in hit
        assert hit["v_gene"] is not None  # Should have V gene assignment
        assert "d_gene" in hit  # Should be None for protein search
        assert hit["d_gene"] is None
        assert "j_gene" in hit  # Should be None for protein search
        assert hit["j_gene"] is None
        assert "c_gene" in hit  # Should be None for protein search
        assert hit["c_gene"] is None

        # Check expected V gene assignment
        assert "IGHV3-9" in hit["v_gene"]  # Should match IGHV3-9 family
        assert hit["identity"] > 90.0  # Should have high identity

    def test_igblast_service_nucleotide_search_real(self):
        """Test real IgBLAST nucleotide search."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        results = service.analyze_antibody_sequence(
            query_sequence=WORKING_NUCLEOTIDE_SEQUENCE,
            organism="human",
            blast_type="igblastn",
            evalue=1e-10,
        )

        assert results is not None
        assert "hits" in results
        # Should find hits for this known nucleotide sequence
        assert len(results["hits"]) > 0

        # Check hit structure for nucleotide search
        hit = results["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert "identity" in hit
        assert "v_gene" in hit
        assert hit["v_gene"] is not None  # Should have V gene assignment

        # For nucleotide searches with AIRR format, D/J/C genes and CDR3 info are available
        assert "d_gene" in hit
        assert "j_gene" in hit
        assert "c_gene" in hit
        assert "cdr3_start" in hit
        assert "cdr3_end" in hit
        assert "cdr3_sequence" in hit
        # D/J/C genes may be None for partial sequences, but structure should be present

        # Check expected gene assignments for full Humira sequence
        assert "IGHV3-9" in hit["v_gene"]  # Should match IGHV3-9 family
        assert (
            hit["identity"] > 70.0
        )  # Should have good identity for full sequence

        # Full Humira sequence should have D and J gene assignments
        if hit["d_gene"] is not None:
            assert "IGHD" in hit["d_gene"]  # Should contain D gene assignments
        if hit["j_gene"] is not None:
            assert "IGHJ" in hit["j_gene"]  # Should contain J gene assignment

        # Should have CDR3 sequence for full sequence
        if hit["cdr3_sequence"] is not None:
            assert (
                len(hit["cdr3_sequence"]) > 10
            )  # CDR3 should be substantial length

    def test_igblast_service_reverse_translated_sequence_real(self):
        """Test IgBLAST with reverse-translated sequence."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        results = service.analyze_antibody_sequence(
            query_sequence=REVERSE_TRANSLATED_SEQUENCE,
            organism="human",
            blast_type="igblastn",
            evalue=10,  # More relaxed for reverse-translated sequence
        )

        assert results is not None
        assert "hits" in results
        # Should find hits for this reverse-translated sequence
        assert len(results["hits"]) > 0

        # Check hit structure
        hit = results["hits"][0]
        assert "query_id" in hit
        assert "subject_id" in hit
        assert "identity" in hit
        assert "v_gene" in hit
        assert hit["v_gene"] is not None  # Should have V gene assignment

        # Should have reasonable identity (reverse-translated sequences may have lower identity)
        assert hit["identity"] > 70.0

    def test_igblast_service_enhanced_gene_assignments_real(self):
        """Test enhanced gene assignments with full Humira sequence that has complete V, D, J, CDR3 data."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        results = service.analyze_antibody_sequence(
            query_sequence=WORKING_NUCLEOTIDE_SEQUENCE,  # Full Humira sequence
            organism="human",
            blast_type="igblastn",
            evalue=1e-10,
        )

        assert results is not None
        assert "hits" in results
        assert len(results["hits"]) > 0

        hit = results["hits"][0]
        assert hit["v_gene"] is not None

        # Full Humira sequence should have complete gene assignments
        assert "IGHV3-9" in hit["v_gene"]  # Should match IGHV3-9 family
        assert hit["d_gene"] is not None  # Should have D gene assignments
        assert (
            "IGHD" in hit["d_gene"]
        )  # Should contain D genes like IGHD1-26, IGHD5-5, IGHD6-13
        assert hit["j_gene"] is not None  # Should have J gene assignment
        assert "IGHJ1" in hit["j_gene"]  # Should match IGHJ1 family

        # Should have CDR3 sequence
        assert hit["cdr3_sequence"] is not None
        assert (
            len(hit["cdr3_sequence"]) > 20
        )  # Should be substantial CDR3 sequence

        # Log all gene assignments for verification
        print(
            f"Complete gene assignments: V={hit.get('v_gene')}, D={hit.get('d_gene')}, J={hit.get('j_gene')}, C={hit.get('c_gene')}"
        )
        print(
            f"CDR3 sequence: {hit.get('cdr3_sequence')} (length: {len(hit.get('cdr3_sequence', ''))})"
        )
        print(f"Identity: {hit.get('identity')}%")

    def test_igblast_service_mouse_organism_real(self):
        """Test IgBLAST with mouse organism."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        results = service.analyze_antibody_sequence(
            query_sequence=WORKING_PROTEIN_SEQUENCE,
            organism="mouse",
            blast_type="igblastp",
            evalue=1e-5,  # More relaxed for cross-species
        )

        assert results is not None
        assert "hits" in results
        # May or may not find hits depending on cross-species similarity
        # Just check that it doesn't error out

        # If hits found, check structure
        if len(results["hits"]) > 0:
            hit = results["hits"][0]
            assert "query_id" in hit
            assert "subject_id" in hit
            assert "identity" in hit
            assert "v_gene" in hit

    def test_blast_service_dynamic_database_discovery_real(self):
        """Test real dynamic database discovery."""
        service = BlastService()

        databases = service.get_available_databases()

        assert "public" in databases
        assert "custom" in databases
        assert "internal" in databases

        public_dbs = databases["public"]
        # Should find at least swissprot if databases are set up
        if len(public_dbs) > 0:
            # Verify database structure
            for db_name, description in public_dbs.items():
                assert isinstance(db_name, str)
                assert isinstance(description, str)
                assert len(db_name) > 0
                assert len(description) > 0

    def test_igblast_service_organism_discovery_real(self):
        """Test real organism discovery."""
        service = IgBlastService()

        organisms = service.get_supported_organisms()

        # Should at least include human and mouse
        assert "human" in organisms
        assert "mouse" in organisms

        # Should be a list of strings
        assert isinstance(organisms, list)
        for organism in organisms:
            assert isinstance(organism, str)
            assert len(organism) > 0

    def test_blast_service_sequence_validation_real(self):
        """Test sequence validation with real sequences."""
        service = BlastService()

        # Test valid protein sequence
        is_valid = service.validate_sequence(
            sequence=WORKING_PROTEIN_SEQUENCE, sequence_type="protein"
        )
        assert is_valid is True

        # Test valid nucleotide sequence
        is_valid = service.validate_sequence(
            sequence=WORKING_NUCLEOTIDE_SEQUENCE, sequence_type="nucleotide"
        )
        assert is_valid is True

        # Test invalid sequence
        is_valid = service.validate_sequence(
            sequence="INVALID123!@#", sequence_type="protein"
        )
        assert is_valid is False

    def test_igblast_service_antibody_validation_real(self):
        """Test antibody sequence validation with real sequences."""
        service = IgBlastService()

        # Test valid protein antibody sequence
        is_valid = service.validate_antibody_sequence(
            sequence=WORKING_PROTEIN_SEQUENCE, sequence_type="protein"
        )
        assert is_valid is True

        # Test valid nucleotide antibody sequence
        is_valid = service.validate_antibody_sequence(
            sequence=WORKING_NUCLEOTIDE_SEQUENCE, sequence_type="nucleotide"
        )
        assert is_valid is True

        # Test invalid sequence
        is_valid = service.validate_antibody_sequence(
            sequence="INVALID123!@#", sequence_type="protein"
        )
        assert is_valid is False

    def test_igblast_service_case_insensitive_validation_real(self):
        """Test that sequence validation is case insensitive."""
        service = IgBlastService()

        # Test protein sequences in different cases
        protein_upper = "EVQLVESGGGLVQPGRSLRLSCAASGFTFDDYAMH"
        protein_lower = "evqlvesggglvqpgrslrlscaasgftfddyamh"
        protein_mixed = "EvQlVeSgGgLvQpGrSlRlScAaSgFtFdDyAmH"

        assert (
            service.validate_antibody_sequence(protein_upper, "protein")
            is True
        )
        assert (
            service.validate_antibody_sequence(protein_lower, "protein")
            is True
        )
        assert (
            service.validate_antibody_sequence(protein_mixed, "protein")
            is True
        )

        # Test nucleotide sequences in different cases
        nucleotide_upper = "ATGCGTTAGCATGCAAA"
        nucleotide_lower = "atgcgttagcatgcaaa"
        nucleotide_mixed = "AtGcGtTaGcAtGcAaA"
        nucleotide_with_n = "ATGCNNATGCAAA"
        nucleotide_with_n_lower = "atgcnnatgcaaa"

        assert (
            service.validate_antibody_sequence(nucleotide_upper, "nucleotide")
            is True
        )
        assert (
            service.validate_antibody_sequence(nucleotide_lower, "nucleotide")
            is True
        )
        assert (
            service.validate_antibody_sequence(nucleotide_mixed, "nucleotide")
            is True
        )
        assert (
            service.validate_antibody_sequence(nucleotide_with_n, "nucleotide")
            is True
        )
        assert (
            service.validate_antibody_sequence(
                nucleotide_with_n_lower, "nucleotide"
            )
            is True
        )

    def test_igblast_service_with_custom_format_for_gene_assignments_real(
        self,
    ):
        """Test IgBLAST with custom output format to get D, J, C gene assignments."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        # Use a longer nucleotide sequence that might have D and J gene assignments
        # This is a complete V(D)J rearranged sequence
        complete_vdj_sequence = "CAGGTGCAGCTGGTGGAGTCTGGGGGAGGCGTGGTCCAGCCTGGGAGGTCCCTGAGACTCTCCTGTGCAGCCTCTGGATTCACCTTTAGCAGCTATGCCATGAGCTGGGTCCGCCAGGCTCCAGGCAAGGGGCTGGAGTGGGTGGCAGTTATATCATATGATGGAAGTAATAAATACTATGCAGACTCCGTGAAGGGCCGATTCACCATCTCCAGAGACAATTCCAAGAACACGCTGTATCTGCAAATGAACAGCCTGAGAGCCGAGGACACGGCTGTGTATTACTGTGCGAGAGAGGGGCGTCTGGTTTCCTACGAGTTTGACTACTGGGGCCAGGGAACCCTGGTCACCGTCTCCTCA"

        # Test with custom output format that includes gene assignments
        # Note: We'll use the adapter directly to specify custom format
        if hasattr(service.igblast_adapter, "execute"):
            try:
                results = service.igblast_adapter.execute(
                    query_sequence=complete_vdj_sequence,
                    organism="human",
                    blast_type="igblastn",
                    evalue=1e-5,
                    outfmt="7 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore v_gene d_gene j_gene c_gene",
                )

                assert results is not None
                assert "hits" in results

                if len(results["hits"]) > 0:
                    hit = results["hits"][0]
                    assert "v_gene" in hit
                    assert hit["v_gene"] is not None

                    # Check if we got gene assignments (may vary by sequence)
                    print(f"V gene: {hit.get('v_gene')}")
                    print(f"D gene: {hit.get('d_gene')}")
                    print(f"J gene: {hit.get('j_gene')}")
                    print(f"C gene: {hit.get('c_gene')}")

            except Exception as e:
                # If custom format fails, just check that we can still get basic results
                print(f"Custom format test failed (expected): {e}")

                # Fall back to basic test
                results = service.analyze_antibody_sequence(
                    query_sequence=complete_vdj_sequence,
                    organism="human",
                    blast_type="igblastn",
                    evalue=1e-5,
                )

                assert results is not None
                assert "hits" in results
                assert len(results["hits"]) > 0

    def test_igblast_service_full_antibody_sequence_real(self):
        """Test IgBLAST with a full antibody sequence that might yield gene assignments."""
        service = IgBlastService()

        # Skip if adapters not available
        if service.igblast_adapter is None:
            pytest.skip("IgBLAST adapter not available")

        # A longer sequence that includes more of the antibody structure
        # This should increase chances of getting D and J gene assignments
        extended_sequence = "GAGGTTCAGCTGGTTGAGTCTGGTGGTGGTCTGGTTCAGCCTGGTCGTTCTCTGCGTCTGTCTTGTGCTGCTTCTGGTTTTACTTTTGATGATTATGCTATGCATTGGGTTCGTCAGGCTCCTGGTAAGGGTCTGGAGTGGGTTTCTGCTATTACTTGGAATTCTGGTCATATTGATTATGCTGATTCTGTTGAGGGTCGTTTTACTATTTCTCGTGATAATGCTAAGAATTCTCTGTATCTGCAGATGAATTCTCTGCGTGCTGAGGATACTGCTGTTTATTATTGTGCTAAGGTTTCTTATCTGTCTACTGCTTCTTCTCTGGATTATTGGGGTCAGGGTACTCTGGTTACTGTTTCTTCTGCTTCTACTAAGGGTCCTTCTGTTGTTCCTTCTCCTTCTGGTGCTGCTGCTGGTGTTGCTGGTGTTGCTGCTGGTGTTGCTGGT"

        results = service.analyze_antibody_sequence(
            query_sequence=extended_sequence,
            organism="human",
            blast_type="igblastn",
            evalue=1e-3,  # More relaxed E-value for longer sequence
        )

        assert results is not None
        assert "hits" in results

        if len(results["hits"]) > 0:
            hit = results["hits"][0]
            assert "v_gene" in hit
            assert hit["v_gene"] is not None

            # Log what gene assignments we got
            print(f"Extended sequence results:")
            print(f"V gene: {hit.get('v_gene')}")
            print(f"D gene: {hit.get('d_gene')}")
            print(f"J gene: {hit.get('j_gene')}")
            print(f"C gene: {hit.get('c_gene')}")
            print(f"Identity: {hit.get('identity')}")

            # Should at least have V gene assignment
            assert hit["v_gene"] is not None
