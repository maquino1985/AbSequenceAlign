"""
Comprehensive integration tests for alignment, MSA, and PSSM functionality.
Tests actual alignment functionality with real sequences and no mocking.
"""

import pytest
import subprocess
from backend.logger import logger
from backend.annotation.alignment_engine import AlignmentEngine
from backend.msa.msa_engine import MSAEngine
from backend.msa.pssm_calculator import PSSMCalculator
from backend.models.models import (
    AlignmentMethod,
    NumberingScheme,
    MSAResult,
    MSASequence,
)


@pytest.fixture
def alignment_engine():
    """Create an AlignmentEngine instance"""
    return AlignmentEngine()


@pytest.fixture
def msa_engine():
    """Create an MSAEngine instance"""
    return MSAEngine()


@pytest.fixture
def pssm_calculator():
    """Create a PSSMCalculator instance"""
    return PSSMCalculator()


@pytest.fixture
def real_antibody_sequences():
    """Real antibody sequences for testing alignment"""
    return [
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
        "QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
    ]


@pytest.fixture
def diverse_sequences():
    """Diverse sequences for testing alignment robustness"""
    return [
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
        "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
        "QSVLTQPPSVSGAPGQRVTISCTGSSSNIGSGYDVHWYQDLPGTAPKLLIYGNSKRPSGVPDRFSGSKSGTSASLAITGLQSEDEADYYCASWTDGLSLVVFGGGTKLTVLG",
    ]


@pytest.fixture
def msa_test_sequences():
    """Sequences for MSA testing with names"""
    return [
        (
            "heavy_chain_1",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
        ),
        (
            "heavy_chain_2",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
        ),
        (
            "light_chain_1",
            "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS",
        ),
    ]


class TestAlignmentEngine:
    """Tests for AlignmentEngine functionality"""

    def test_alignment_engine_initialization(self, alignment_engine):
        """Test AlignmentEngine initialization"""
        assert alignment_engine is not None
        assert hasattr(alignment_engine, "available_matrices")
        assert "BLOSUM62" in alignment_engine.available_matrices
        assert len(alignment_engine.available_matrices) > 0

    def test_align_sequences_invalid_method(
        self, alignment_engine, real_antibody_sequences
    ):
        """Test alignment with invalid method"""
        with pytest.raises(ValueError, match="Unsupported alignment method"):
            alignment_engine.align_sequences(
                real_antibody_sequences, "invalid_method"
            )

    def test_align_sequences_single_sequence(self, alignment_engine):
        """Test alignment with single sequence"""
        with pytest.raises(ValueError, match="At least 2 sequences required"):
            alignment_engine.align_sequences(
                [
                    "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"
                ],
                AlignmentMethod.PAIRWISE_GLOBAL,
            )

    def test_pairwise_global_alignment_with_real_sequences(
        self, alignment_engine, real_antibody_sequences
    ):
        """Test global pairwise alignment with real antibody sequences"""
        result = alignment_engine.align_sequences(
            real_antibody_sequences,
            AlignmentMethod.PAIRWISE_GLOBAL,
            gap_open=-10.0,
            gap_extend=-0.5,
        )

        assert result is not None
        assert result["method"] == "pairwise_global"
        assert "score" in result
        assert "identity" in result
        assert "length" in result
        assert "gaps" in result

        # Verify realistic values for antibody sequences
        assert result["identity"] > 0.0  # Should have some similarity
        assert result["identity"] <= 1.0  # Should not exceed 100%
        assert result["length"] >= max(
            len(seq) for seq in real_antibody_sequences
        )  # Should be at least as long as longest sequence
        assert result["gaps"] >= 0  # Should have non-negative gaps

        # Parse alignment to verify sequences have same length
        alignment_str = result["alignment"]
        aligned_seq1, aligned_seq2 = alignment_engine._parse_alignment_string(
            alignment_str
        )
        assert len(aligned_seq1) == len(
            aligned_seq2
        ), "Aligned sequences must have same length"
        assert len(aligned_seq1) == result["length"]

    def test_pairwise_local_alignment_with_real_sequences(
        self, alignment_engine, real_antibody_sequences
    ):
        """Test local pairwise alignment with real antibody sequences"""
        result = alignment_engine.align_sequences(
            real_antibody_sequences,
            AlignmentMethod.PAIRWISE_LOCAL,
            gap_open=-10.0,
            gap_extend=-0.5,
        )

        assert result is not None
        assert result["method"] == "pairwise_local"
        assert "score" in result
        assert "identity" in result
        assert "length" in result
        assert "gaps" in result

        # Local alignment should find high-similarity regions
        assert result["identity"] > 0.0
        assert result["identity"] <= 1.0

        # Parse alignment to verify sequences have same length
        alignment_str = result["alignment"]
        aligned_seq1, aligned_seq2 = alignment_engine._parse_alignment_string(
            alignment_str
        )
        assert len(aligned_seq1) == len(
            aligned_seq2
        ), "Aligned sequences must have same length"
        assert len(aligned_seq1) == result["length"]

    def test_pairwise_alignment_too_many_sequences(self, alignment_engine):
        """Test pairwise alignment with too many sequences"""
        sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            "QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
            "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
        ]
        with pytest.raises(
            ValueError, match="Pairwise alignment requires exactly 2 sequences"
        ):
            alignment_engine.align_sequences(
                sequences, AlignmentMethod.PAIRWISE_GLOBAL
            )

    def test_pairwise_global_alignment_invalid_matrix(
        self, alignment_engine, real_antibody_sequences
    ):
        """Test global pairwise alignment with invalid matrix"""
        with pytest.raises(
            ValueError, match="Unsupported substitution matrix"
        ):
            alignment_engine.align_sequences(
                real_antibody_sequences,
                AlignmentMethod.PAIRWISE_GLOBAL,
                matrix="INVALID_MATRIX",
            )

    def test_calculate_identity_with_real_sequences(self, alignment_engine):
        """Test sequence identity calculation with real sequences"""
        # Test with similar antibody sequences
        seq1 = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"
        seq2 = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"

        identity = alignment_engine._calculate_identity(seq1, seq2)
        assert 0.0 <= identity <= 1.0
        assert identity > 0.5  # Should have significant similarity

    def test_calculate_identity_with_gaps(self, alignment_engine):
        """Test sequence identity calculation with gaps"""
        seq1 = "EVQLVESGGGLVQPGGSLRLSCAAS--TFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"
        seq2 = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"

        identity = alignment_engine._calculate_identity(seq1, seq2)
        assert 0.0 <= identity <= 1.0
        assert identity > 0.8  # Should still have high identity despite gaps

    def test_calculate_identity_different_lengths(self, alignment_engine):
        """Test identity calculation with sequences of different lengths after alignment"""
        seq1 = "EVQLVESGGGLVQPGQSLRLSCAAS"
        seq2 = "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"

        # First align the sequences to get equal-length gapped sequences
        alignment_result = alignment_engine.align_sequences(
            [seq1, seq2],
            AlignmentMethod.PAIRWISE_GLOBAL,
            gap_open=-10.0,
            gap_extend=-0.5,
            matrix="BLOSUM62",
        )

        # Parse the alignment to get individual aligned sequences
        alignment_str = alignment_result["alignment"]
        aligned_seq1, aligned_seq2 = alignment_engine._parse_alignment_string(
            alignment_str
        )
        logger.info(f"Aligned sequences: {aligned_seq1}, {aligned_seq2}")
        # Verify the aligned sequences have the same length
        assert len(aligned_seq1) == len(
            aligned_seq2
        ), "Aligned sequences must have same length"

        # Now calculate identity on the aligned sequences
        identity = alignment_engine._calculate_identity(
            aligned_seq1, aligned_seq2
        )
        logger.info(f"Identity: {identity}")
        # Should have some identity since they share a common prefix
        assert 0.0 <= identity <= 1.0
        assert (
            identity > 0.0
        )  # Should have some similarity due to common prefix
        assert (
            identity < 1.0
        )  # Should not be 100% identical due to length difference

    def test_calculate_msa_identity_with_real_sequences(
        self, alignment_engine, diverse_sequences
    ):
        """Test MSA identity calculation with real sequences"""
        identity = alignment_engine._calculate_msa_identity(diverse_sequences)
        assert 0.0 <= identity <= 1.0
        assert identity > 0.0  # Should have some similarity

    def test_calculate_msa_identity_single_sequence(self, alignment_engine):
        """Test MSA identity calculation with single sequence"""
        sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"
        ]
        identity = alignment_engine._calculate_msa_identity(sequences)
        assert identity == 0.0

    def test_parse_alignment_with_real_sequences(self, alignment_engine):
        """Test alignment parsing with real sequences"""
        alignment_content = ">heavy_chain\nEVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS\n>light_chain\nDIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK\n"
        sequences = alignment_engine._parse_alignment(alignment_content)
        assert len(sequences) == 2
        assert (
            sequences[0]
            == "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"
        )
        assert (
            sequences[1]
            == "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK"
        )

    def test_parse_alignment_empty(self, alignment_engine):
        """Test parsing empty alignment"""
        sequences = alignment_engine._parse_alignment("")
        assert len(sequences) == 0

    def test_parse_alignment_single_sequence(self, alignment_engine):
        """Test parsing single sequence alignment"""
        alignment_content = ">heavy_chain\nEVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS\n"
        sequences = alignment_engine._parse_alignment(alignment_content)
        assert len(sequences) == 1
        assert (
            sequences[0]
            == "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS"
        )

    def test_map_position_to_aligned_with_gaps(self, alignment_engine):
        """Test mapping positions with gaps"""
        original_seq = "EVQLVESGGGLVQPGGSLRLSCAAS"
        aligned_seq = "EVQLVESGGGLVQPGGSLRLSCAAS---"  # Gaps at end
        pos = alignment_engine._map_position_to_aligned(
            20, original_seq, aligned_seq
        )
        assert pos == 20  # Position before gaps

    def test_map_position_to_aligned_end_of_sequence(self, alignment_engine):
        """Test mapping position at end of sequence"""
        original_seq = "EVQLVESGGGLVQPGGSLRLSCAAS"
        aligned_seq = "EVQLVESGGGLVQPGGSLRLSCAAS---"  # Gaps at end
        pos = alignment_engine._map_position_to_aligned(
            24, original_seq, aligned_seq
        )
        assert pos == 24  # Last position before gaps

    def test_map_position_to_aligned_beyond_sequence(self, alignment_engine):
        """Test mapping position beyond sequence length"""
        original_seq = "EVQLVESGGGLVQPGGSLRLSCAAS"
        aligned_seq = "EVQLVESGGGLVQPGGSLRLSCAAS---"  # Gaps at end
        pos = alignment_engine._map_position_to_aligned(
            30, original_seq, aligned_seq
        )
        assert pos == len(aligned_seq) - 1  # Should return last position

    def test_antibody_aware_alignment_with_real_sequences(
        self, alignment_engine, diverse_sequences
    ):
        """Test antibody-aware alignment with real sequences"""
        result = alignment_engine.align_sequences(
            diverse_sequences,
            AlignmentMethod.CUSTOM_ANTIBODY,
            numbering_scheme=NumberingScheme.IMGT,
        )

        assert result is not None
        assert result["method"] == "muscle"  # Should fall back to MUSCLE
        assert "identity" in result
        assert "length" in result
        assert "sequences" in result
        assert result["sequences"] == len(diverse_sequences)

    def test_external_msa_alignment_invalid_method(
        self, alignment_engine, diverse_sequences
    ):
        """Test MSA alignment with invalid method"""
        with pytest.raises(ValueError, match="Unsupported MSA method"):
            alignment_engine._external_msa_alignment(
                diverse_sequences,
                "invalid_method",
                gap_open=-10.0,
                gap_extend=-0.5,
                matrix="BLOSUM62",
            )


class TestMSAEngine:
    """Tests for MSAEngine functionality"""

    def test_msa_engine_initialization(self, msa_engine):
        """Test MSAEngine initialization"""
        assert msa_engine is not None
        assert hasattr(msa_engine, "supported_methods")
        assert len(msa_engine.supported_methods) > 0

    def test_supported_methods(self, msa_engine):
        """Test that all expected alignment methods are supported"""
        expected_methods = [
            AlignmentMethod.MUSCLE,
            AlignmentMethod.MAFFT,
            AlignmentMethod.CLUSTALO,
            AlignmentMethod.PAIRWISE_GLOBAL,
            AlignmentMethod.PAIRWISE_LOCAL,
        ]

        for method in expected_methods:
            assert method in msa_engine.supported_methods

    def test_create_msa_invalid_method(self, msa_engine, msa_test_sequences):
        """Test create_msa with invalid alignment method"""
        with pytest.raises(ValueError, match="Unsupported alignment method"):
            msa_engine.create_msa(msa_test_sequences, "invalid_method")

    def test_create_msa_empty_sequences(self, msa_engine):
        """Test create_msa with empty sequences list"""
        with pytest.raises(ValueError, match="No valid sequences provided"):
            msa_engine.create_msa([], AlignmentMethod.MUSCLE)

    def test_create_alignment_matrix(self, msa_engine):
        """Test _create_alignment_matrix method with real sequences"""
        aligned_sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---",
            "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS",
        ]

        matrix = msa_engine._create_alignment_matrix(aligned_sequences)

        assert len(matrix) == 3
        assert len(matrix[0]) == len(aligned_sequences[0])
        assert matrix[0][0] == "E"
        assert matrix[1][0] == "E"
        assert matrix[2][0] == "E"

    def test_create_alignment_matrix_empty(self, msa_engine):
        """Test _create_alignment_matrix with empty sequences"""
        matrix = msa_engine._create_alignment_matrix([])
        assert matrix == []

    def test_generate_consensus(self, msa_engine):
        """Test _generate_consensus method with real sequences"""
        alignment_matrix = [
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            ),
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
            ),
            list(
                "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS"
            ),
        ]

        consensus = msa_engine._generate_consensus(alignment_matrix)

        assert len(consensus) == len(alignment_matrix[0])
        assert consensus[0] == "E"  # All sequences start with E
        assert consensus[1] == "V"  # All sequences have V at position 1

    def test_generate_consensus_empty(self, msa_engine):
        """Test _generate_consensus with empty matrix"""
        consensus = msa_engine._generate_consensus([])
        assert consensus == ""

    def test_align_muscle_success(self, msa_engine):
        """Test MUSCLE alignment with real sequences"""
        sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
        ]

        result = msa_engine._align_muscle(sequences)

        assert len(result) == 2
        assert len(result[0]) > 0
        assert len(result[1]) > 0
        # Verify aligned sequences have same length
        assert len(result[0]) == len(result[1])

    def test_align_pairwise_global_single_sequence(self, msa_engine):
        """Test pairwise global alignment with single sequence"""
        sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
        ]

        result = msa_engine._align_pairwise_global(sequences)

        assert len(result) == 1
        assert result[0] == sequences[0]

    def test_align_pairwise_local_single_sequence(self, msa_engine):
        """Test pairwise local alignment with single sequence"""
        sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
        ]

        result = msa_engine._align_pairwise_local(sequences)

        assert len(result) == 1
        assert result[0] == sequences[0]

    def test_create_msa_result_structure(self, msa_engine, msa_test_sequences):
        """Test that create_msa returns proper MSAResult structure with real sequences"""
        result = msa_engine.create_msa(
            msa_test_sequences, AlignmentMethod.MUSCLE
        )

        assert isinstance(result, MSAResult)
        assert result.msa_id is not None
        assert len(result.sequences) == 3
        assert result.alignment_method == AlignmentMethod.MUSCLE
        assert result.consensus is not None
        assert len(result.alignment_matrix) == 3
        assert result.created_at is not None
        assert result.metadata is not None
        assert result.metadata["num_sequences"] == 3

        # Verify all aligned sequences have same length
        aligned_lengths = [
            len(seq.aligned_sequence) for seq in result.sequences
        ]
        assert (
            len(set(aligned_lengths)) == 1
        ), "All aligned sequences must have same length"

    def test_msa_sequence_structure(self, msa_engine, msa_test_sequences):
        """Test that MSASequence objects are created correctly with real sequences"""
        result = msa_engine.create_msa(
            msa_test_sequences, AlignmentMethod.MUSCLE
        )

        for i, msa_seq in enumerate(result.sequences):
            assert isinstance(msa_seq, MSASequence)
            assert msa_seq.name == msa_test_sequences[i][0]
            assert msa_seq.original_sequence == msa_test_sequences[i][1]
            assert len(msa_seq.aligned_sequence) > 0
            assert msa_seq.start_position == 0
            assert msa_seq.end_position == len(msa_seq.aligned_sequence)
            assert isinstance(msa_seq.gaps, list)

    def test_gap_detection(self, msa_engine, msa_test_sequences):
        """Test that gaps are correctly detected in aligned sequences"""
        result = msa_engine.create_msa(
            msa_test_sequences, AlignmentMethod.MUSCLE
        )

        # Check that gaps are detected in sequences
        for msa_seq in result.sequences:
            assert isinstance(msa_seq.gaps, list)
            # Verify gap positions are valid
            for gap_pos in msa_seq.gaps:
                assert 0 <= gap_pos < len(msa_seq.aligned_sequence)
                assert msa_seq.aligned_sequence[gap_pos] == "-"

    def test_msa_with_different_methods(self, msa_engine, msa_test_sequences):
        """Test MSA creation with different alignment methods"""
        methods = [
            AlignmentMethod.MUSCLE,
            AlignmentMethod.MAFFT,
            AlignmentMethod.CLUSTALO,
        ]

        for method in methods:
            try:
                result = msa_engine.create_msa(msa_test_sequences, method)

                assert isinstance(result, MSAResult)
                assert result.alignment_method == method
                assert len(result.sequences) == 3

                # Verify all sequences have same length
                aligned_lengths = [
                    len(seq.aligned_sequence) for seq in result.sequences
                ]
                assert (
                    len(set(aligned_lengths)) == 1
                ), f"All aligned sequences must have same length for method {method}"

            except (
                RuntimeError,
                subprocess.CalledProcessError,
                FileNotFoundError,
            ) as e:
                # Skip test if external tool is not available or fails
                logger.warning(
                    f"External tool for method {method} not available or failed: {e}"
                )
                pytest.skip(f"External tool for method {method} not available or failed: {e}")


class TestPSSMCalculator:
    """Tests for PSSM calculation functionality"""

    def test_pssm_calculator_initialization(self, pssm_calculator):
        """Test PSSMCalculator initialization"""
        assert pssm_calculator is not None
        assert hasattr(pssm_calculator, "amino_acids")
        assert hasattr(pssm_calculator, "background_frequencies")
        assert len(pssm_calculator.amino_acids) == 20
        assert len(pssm_calculator.background_frequencies) == 20

    def test_pssm_calculation_with_real_sequences(self, pssm_calculator):
        """Test PSSM calculation with real antibody sequences"""
        # Create alignment matrix with real sequences
        alignment_matrix = [
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"
            ),
            list(
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
            ),
            list(
                "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS"
            ),
        ]

        # Calculate PSSM
        pssm_data = pssm_calculator.calculate_pssm(alignment_matrix)

        # Verify PSSM structure
        assert pssm_data is not None
        assert "position_frequencies" in pssm_data
        assert "position_scores" in pssm_data
        assert "conservation_scores" in pssm_data
        assert "consensus" in pssm_data
        assert "amino_acids" in pssm_data
        assert "alignment_length" in pssm_data
        assert "num_sequences" in pssm_data

        # Verify data integrity
        assert (
            len(pssm_data["position_frequencies"])
            == pssm_data["alignment_length"]
        )
        assert (
            len(pssm_data["position_scores"]) == pssm_data["alignment_length"]
        )
        assert (
            len(pssm_data["conservation_scores"])
            == pssm_data["alignment_length"]
        )
        assert len(pssm_data["consensus"]) == pssm_data["alignment_length"]
        assert pssm_data["num_sequences"] == 3

        # Verify amino acid coverage
        assert len(pssm_data["amino_acids"]) == 20  # Standard amino acids
        assert "A" in pssm_data["amino_acids"]
        assert "R" in pssm_data["amino_acids"]

        # Verify position frequencies sum to approximately 1.0
        for pos_freq in pssm_data["position_frequencies"]:
            total_freq = sum(pos_freq.values())
            assert 0.95 <= total_freq <= 1.05  # Allow small numerical errors

        # Verify conservation scores are between 0 and 1
        for score in pssm_data["conservation_scores"]:
            assert 0 <= score <= 1

    def test_pssm_calculation_empty_alignment(self, pssm_calculator):
        """Test PSSM calculation with empty alignment"""
        pssm_data = pssm_calculator.calculate_pssm([])

        assert pssm_data is not None
        assert "position_frequencies" in pssm_data
        assert "position_scores" in pssm_data
        assert "conservation_scores" in pssm_data
        assert "consensus" in pssm_data
        assert len(pssm_data["position_frequencies"]) == 0

    def test_pssm_integration_with_msa(
        self, msa_engine, pssm_calculator, msa_test_sequences
    ):
        """Test PSSM calculation integration with MSA results"""
        # Create MSA
        msa_result = msa_engine.create_msa(
            msa_test_sequences, AlignmentMethod.MUSCLE
        )

        # Calculate PSSM from MSA alignment matrix
        pssm_data = pssm_calculator.calculate_pssm(msa_result.alignment_matrix)

        # Verify PSSM data matches MSA structure
        assert len(pssm_data["position_frequencies"]) == len(
            msa_result.alignment_matrix[0]
        )
        assert len(pssm_data["conservation_scores"]) == len(
            msa_result.alignment_matrix[0]
        )
        assert len(pssm_data["consensus"]) == len(
            msa_result.alignment_matrix[0]
        )
        assert pssm_data["num_sequences"] == len(msa_result.alignment_matrix)

        # Verify PSSM data is in MSA metadata
        assert "pssm_data" in msa_result.metadata
        msa_pssm = msa_result.metadata["pssm_data"]
        assert len(msa_pssm["position_frequencies"]) == len(
            pssm_data["position_frequencies"]
        )


class TestIntegration:
    """Integration tests combining alignment, MSA, and PSSM functionality"""

    def test_complete_workflow_with_real_sequences(
        self, alignment_engine, msa_engine, pssm_calculator, diverse_sequences
    ):
        """Test complete workflow from alignment to MSA to PSSM with real sequences"""
        # Step 1: Perform pairwise alignment
        alignment_result = alignment_engine.align_sequences(
            diverse_sequences[:2],  # Use first two sequences
            AlignmentMethod.PAIRWISE_GLOBAL,
        )

        # Verify alignment
        assert alignment_result["method"] == "pairwise_global"
        assert alignment_result["identity"] > 0.0

        # Step 2: Create MSA with all sequences
        msa_sequences = [
            ("seq1", diverse_sequences[0]),
            ("seq2", diverse_sequences[1]),
            ("seq3", diverse_sequences[2]),
        ]
        msa_result = msa_engine.create_msa(
            msa_sequences, AlignmentMethod.MUSCLE
        )

        # Verify MSA
        assert len(msa_result.sequences) == 3
        assert len(msa_result.alignment_matrix) == 3

        # Step 3: Calculate PSSM from MSA
        pssm_data = pssm_calculator.calculate_pssm(msa_result.alignment_matrix)

        # Verify PSSM
        assert len(pssm_data["position_frequencies"]) == len(
            msa_result.alignment_matrix[0]
        )
        assert pssm_data["num_sequences"] == 3

        # Step 4: Verify all aligned sequences have same length
        aligned_lengths = [
            len(seq.aligned_sequence) for seq in msa_result.sequences
        ]
        assert (
            len(set(aligned_lengths)) == 1
        ), "All aligned sequences must have same length"

        # Step 5: Verify identity calculations are consistent
        msa_identity = alignment_engine._calculate_msa_identity(
            [seq.aligned_sequence for seq in msa_result.sequences]
        )
        assert 0.0 <= msa_identity <= 1.0

    def test_alignment_consistency_across_methods(
        self, alignment_engine, msa_engine, real_antibody_sequences
    ):
        """Test that alignment results are consistent across different methods"""
        # Test pairwise alignment
        pairwise_result = alignment_engine.align_sequences(
            real_antibody_sequences, AlignmentMethod.PAIRWISE_GLOBAL
        )

        # Test MSA alignment
        msa_sequences = [
            ("seq1", real_antibody_sequences[0]),
            ("seq2", real_antibody_sequences[1]),
        ]
        msa_result = msa_engine.create_msa(
            msa_sequences, AlignmentMethod.MUSCLE
        )

        # Both should produce valid alignments
        assert pairwise_result["identity"] > 0.0
        assert len(msa_result.sequences) == 2

        # Both should have aligned sequences of same length
        pairwise_aligned = alignment_engine._parse_alignment_string(
            pairwise_result["alignment"]
        )
        assert len(pairwise_aligned[0]) == len(pairwise_aligned[1])

        msa_aligned_lengths = [
            len(seq.aligned_sequence) for seq in msa_result.sequences
        ]
        assert len(set(msa_aligned_lengths)) == 1
