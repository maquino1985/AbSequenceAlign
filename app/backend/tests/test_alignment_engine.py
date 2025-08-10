import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from Bio.Align import PairwiseAligner
from backend.annotation.alignment_engine import AlignmentEngine
from backend.models.models import AlignmentMethod, NumberingScheme


@pytest.fixture
def mock_run():
    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def alignment_engine():
    """Create an AlignmentEngine instance"""
    return AlignmentEngine()


@pytest.fixture
def test_sequences():
    """Test sequences for alignment"""
    return [
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
        "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
    ]


def test_alignment_engine_initialization():
    """Test AlignmentEngine initialization"""
    engine = AlignmentEngine()
    assert engine is not None
    assert hasattr(engine, "available_matrices")
    assert "BLOSUM62" in engine.available_matrices


def test_align_sequences_invalid_method(alignment_engine, test_sequences):
    """Test alignment with invalid method"""
    with pytest.raises(ValueError, match="Unsupported alignment method"):
        alignment_engine.align_sequences(test_sequences, "invalid_method")


def test_align_sequences_single_sequence(alignment_engine):
    """Test alignment with single sequence"""
    with pytest.raises(ValueError, match="At least 2 sequences required"):
        alignment_engine.align_sequences(["SEQUENCE"], AlignmentMethod.PAIRWISE_GLOBAL)


def test_pairwise_global_alignment(alignment_engine):
    """Test global pairwise alignment"""
    # Use identical sequences to ensure non-zero identity
    sequences = ["ABCDEF", "ABCDEF"]

    # Mock PairwiseAligner
    with patch("Bio.Align.PairwiseAligner") as mock_aligner:
        mock_instance = MagicMock()
        mock_alignment = MagicMock()
        mock_alignment.score = 100.0
        mock_alignment.__str__.return_value = (
            f"{sequences[0]}\n{sequences[0]}\n"  # Add newline
        )
        mock_instance.align.return_value = [mock_alignment]
        mock_aligner.return_value = mock_instance

        # Mock identity calculation
        with patch.object(alignment_engine, "_calculate_identity", return_value=1.0):
            result = alignment_engine.align_sequences(
                sequences,
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
            assert result["identity"] == 1.0  # Identical sequences
            assert result["length"] == len(sequences[0])  # No gaps


def test_pairwise_global_alignment_invalid_matrix(alignment_engine, test_sequences):
    """Test global pairwise alignment with invalid matrix"""
    with pytest.raises(ValueError, match="Unsupported substitution matrix"):
        alignment_engine.align_sequences(
            test_sequences, AlignmentMethod.PAIRWISE_GLOBAL, matrix="INVALID_MATRIX"
        )


def test_pairwise_global_alignment_no_alignment(alignment_engine):
    """Test global pairwise alignment when no alignment is found"""
    # Mock PairwiseAligner to return an empty iterator
    with patch("Bio.Align.PairwiseAligner") as mock_aligner:
        mock_instance = MagicMock()
        mock_instance.mode = "global"
        mock_instance.substitution_matrix = None
        mock_instance.open_gap_score = -10.0
        mock_instance.extend_gap_score = -0.5
        mock_instance.align.return_value = []  # Empty list
        mock_aligner.return_value = mock_instance

        # Mock list() to return an empty list
        with patch("builtins.list", return_value=[]):
            # Mock identity calculation to avoid interference
            with patch.object(
                alignment_engine, "_calculate_identity", return_value=0.0
            ):
                with pytest.raises(RuntimeError, match="No alignment found"):
                    alignment_engine._pairwise_global_alignment(
                        ["AAAAAAAA", "TTTTTTTT"],
                        gap_open=-10.0,
                        gap_extend=-0.5,
                        matrix="BLOSUM62",
                    )


def test_pairwise_local_alignment(alignment_engine, test_sequences):
    """Test local pairwise alignment"""
    result = alignment_engine.align_sequences(
        test_sequences, AlignmentMethod.PAIRWISE_LOCAL, gap_open=-10.0, gap_extend=-0.5
    )

    assert result is not None
    assert result["method"] == "pairwise_local"
    assert "score" in result
    assert "identity" in result
    assert "length" in result
    assert "gaps" in result


def test_pairwise_alignment_too_many_sequences(alignment_engine):
    """Test pairwise alignment with too many sequences"""
    sequences = ["SEQ1", "SEQ2", "SEQ3"]
    with pytest.raises(
        ValueError, match="Pairwise alignment requires exactly 2 sequences"
    ):
        alignment_engine.align_sequences(sequences, AlignmentMethod.PAIRWISE_GLOBAL)


@patch("subprocess.run")
def test_muscle_alignment(mock_run, alignment_engine, test_sequences):
    """Test MUSCLE alignment"""
    # Mock successful MUSCLE run
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = ">seq1\nALIGNED1\n>seq2\nALIGNED2\n"
    mock_run.return_value = mock_process

    result = alignment_engine.align_sequences(
        test_sequences, AlignmentMethod.MUSCLE, gap_open=-10.0, gap_extend=-0.5
    )

    assert result is not None
    assert result["method"] == "muscle"
    assert "identity" in result
    assert "length" in result
    assert "sequences" in result


@patch("subprocess.run")
def test_muscle_alignment_failure(mock_run, alignment_engine, test_sequences):
    """Test MUSCLE alignment failure"""
    # Mock failed MUSCLE run
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.stderr = "Error running MUSCLE"
    mock_run.return_value = mock_process

    with pytest.raises(RuntimeError, match="External alignment failed"):
        alignment_engine.align_sequences(
            test_sequences, AlignmentMethod.MUSCLE, gap_open=-10.0, gap_extend=-0.5
        )


@patch("subprocess.run")
def test_mafft_alignment(mock_run, alignment_engine, test_sequences):
    """Test MAFFT alignment"""
    # Mock successful MAFFT run
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = ">seq1\nALIGNED1\n>seq2\nALIGNED2\n"
    mock_run.return_value = mock_process

    result = alignment_engine.align_sequences(
        test_sequences, AlignmentMethod.MAFFT, gap_open=-10.0, gap_extend=-0.5
    )

    assert result is not None
    assert result["method"] == "mafft"
    assert "identity" in result
    assert "length" in result
    assert "sequences" in result


@patch("subprocess.run")
def test_clustalo_alignment(mock_run, alignment_engine, test_sequences):
    """Test Clustal Omega alignment"""
    # Mock successful Clustal Omega run
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = ">seq1\nALIGNED1\n>seq2\nALIGNED2\n"
    mock_run.return_value = mock_process

    result = alignment_engine.align_sequences(
        test_sequences, AlignmentMethod.CLUSTALO, gap_open=-10.0, gap_extend=-0.5
    )

    assert result is not None
    assert result["method"] == "clustalo"
    assert "identity" in result
    assert "length" in result
    assert "sequences" in result


def test_antibody_aware_alignment(alignment_engine, test_sequences):
    """Test antibody-aware alignment (currently falls back to MUSCLE)"""
    with patch(
        "backend.annotation.alignment_engine.AlignmentEngine._external_msa_alignment"
    ) as mock_msa:
        mock_msa.return_value = {
            "method": "muscle",
            "alignment": "test",
            "identity": 0.9,
            "length": 100,
            "sequences": 2,
        }

        result = alignment_engine.align_sequences(
            test_sequences,
            AlignmentMethod.CUSTOM_ANTIBODY,
            numbering_scheme=NumberingScheme.IMGT,
        )

        assert result is not None
        assert result["method"] == "muscle"
        assert mock_msa.called


def test_calculate_identity(alignment_engine):
    """Test sequence identity calculation"""
    seq1 = "ABCDEF-GHI"
    seq2 = "ABCXEF-GHI"
    identity = alignment_engine._calculate_identity(seq1, seq2)
    assert 0.0 <= identity <= 1.0
    assert abs(identity - 0.889) < 0.001  # 8 matches out of 9 non-gap positions


def test_calculate_identity_different_lengths(alignment_engine):
    """Test identity calculation with different sequence lengths"""
    seq1 = "ABCDEF"
    seq2 = "ABCDEFGHI"
    identity = alignment_engine._calculate_identity(seq1, seq2)
    assert identity == 0.0


def test_calculate_msa_identity(alignment_engine):
    """Test MSA identity calculation"""
    sequences = ["ABCDEF-GHI", "ABCXEF-GHI", "ABCDEF-GHX"]
    identity = alignment_engine._calculate_msa_identity(sequences)
    assert 0.0 <= identity <= 1.0


def test_calculate_msa_identity_single_sequence(alignment_engine):
    """Test MSA identity calculation with single sequence"""
    sequences = ["ABCDEF"]
    identity = alignment_engine._calculate_msa_identity(sequences)
    assert identity == 0.0


def test_parse_alignment(alignment_engine):
    """Test alignment parsing"""
    alignment_content = ">seq1\nABCDEF\n>seq2\nGHIJKL\n"
    sequences = alignment_engine._parse_alignment(alignment_content)
    assert len(sequences) == 2
    assert sequences[0] == "ABCDEF"
    assert sequences[1] == "GHIJKL"


def test_parse_alignment_empty(alignment_engine):
    """Test parsing empty alignment"""
    sequences = alignment_engine._parse_alignment("")
    assert len(sequences) == 0


def test_parse_alignment_single_sequence(alignment_engine):
    """Test parsing single sequence alignment"""
    alignment_content = ">seq1\nABCDEF\n"
    sequences = alignment_engine._parse_alignment(alignment_content)
    assert len(sequences) == 1
    assert sequences[0] == "ABCDEF"


def test_external_msa_alignment_invalid_method(
    mock_run, alignment_engine, test_sequences
):
    """Test MSA alignment with invalid method"""
    with pytest.raises(ValueError, match="Unsupported MSA method"):
        alignment_engine._external_msa_alignment(
            test_sequences,
            "invalid_method",
            gap_open=-10.0,
            gap_extend=-0.5,
            matrix="BLOSUM62",
        )


def test_external_msa_alignment_cleanup(mock_run, alignment_engine, test_sequences):
    """Test MSA alignment file cleanup"""
    # Mock successful MSA run
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = ">seq1\nALIGNED1\n>seq2\nALIGNED2\n"
    mock_run.return_value = mock_process

    # Mock tempfile to track created files
    temp_files = []

    def mock_named_temp(mode, suffix, delete):
        temp = MagicMock()
        temp.name = f"/tmp/test{len(temp_files)}{suffix}"
        temp_files.append(temp.name)
        temp.__enter__ = MagicMock(return_value=temp)
        temp.__exit__ = MagicMock()
        temp.write = MagicMock()
        return temp

    with patch("tempfile.NamedTemporaryFile", side_effect=mock_named_temp):
        with patch("os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda x: x in temp_files

            with patch("os.unlink") as mock_unlink:
                with patch("builtins.open", create=True) as mock_open:
                    mock_file = MagicMock()
                    mock_file.__enter__ = MagicMock(return_value=mock_file)
                    mock_file.__exit__ = MagicMock()
                    mock_file.read = MagicMock(
                        return_value=">seq1\nALIGNED1\n>seq2\nALIGNED2\n"
                    )
                    mock_open.return_value = mock_file

                    result = alignment_engine._external_msa_alignment(
                        test_sequences,
                        AlignmentMethod.MUSCLE,
                        gap_open=-10.0,
                        gap_extend=-0.5,
                        matrix="BLOSUM62",
                    )
                    assert result is not None
                    # Check that files were cleaned up
                    assert mock_unlink.call_count == 2
                    mock_unlink.assert_any_call(temp_files[0])
                    mock_unlink.assert_any_call(temp_files[1])


def test_map_position_to_aligned_with_gaps(alignment_engine):
    """Test mapping positions with gaps"""
    original_seq = "ABCDEF"
    aligned_seq = "ABC-DEF"  # Gap after C
    pos = alignment_engine._map_position_to_aligned(2, original_seq, aligned_seq)
    assert pos == 2  # Position before gap


def test_map_position_to_aligned_end_of_sequence(alignment_engine):
    """Test mapping position at end of sequence"""
    original_seq = "ABCDEF"
    aligned_seq = "ABCDEF--"  # Gaps at end
    pos = alignment_engine._map_position_to_aligned(5, original_seq, aligned_seq)
    assert pos == 5  # Last position before gaps


def test_map_position_to_aligned_beyond_sequence(alignment_engine):
    """Test mapping position beyond sequence length"""
    original_seq = "ABCDEF"
    aligned_seq = "ABCDEF--"  # Gaps at end
    pos = alignment_engine._map_position_to_aligned(10, original_seq, aligned_seq)
    assert pos == len(aligned_seq) - 1  # Should return last position
# Test comment to trigger CI
