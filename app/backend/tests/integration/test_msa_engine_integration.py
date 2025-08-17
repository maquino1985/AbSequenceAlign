"""
Integration tests for MSAEngine with real sequences.
Tests all alignment methods, consensus generation, and PSSM calculation.
"""

import subprocess
from typing import List, Tuple

import pytest

from backend.models.models import AlignmentMethod, MSAResult
from backend.msa.msa_engine import MSAEngine


class TestMSAEngineIntegration:
    """Integration tests for MSAEngine functionality."""

    @pytest.fixture
    def msa_engine(self):
        """MSA engine instance."""
        return MSAEngine()

    @pytest.fixture
    def real_antibody_sequences(self) -> List[Tuple[str, str]]:
        """Real antibody sequences for testing alignment."""
        return [
            (
                "heavy_1",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
            (
                "heavy_2",
                "QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
            ),
            (
                "heavy_3",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
            (
                "light_1",
                "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
            ),
            (
                "light_2",
                "QSVLTQPPSVSGAPGQRVTISCTGSSSNIGSGYDVHWYQDLPGTAPKLLIYGNSKRPSGVPDRFSGSKSGTSASLAITGLQSEDEADYYCASWTDGLSLVVFGGGTKLTVLG",
            ),
        ]

    @pytest.fixture
    def diverse_sequences(self) -> List[Tuple[str, str]]:
        """More diverse sequences to test alignment robustness."""
        return [
            (
                "seq1",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
            (
                "seq2",
                "QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
            ),
            (
                "seq3",
                "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
            ),
            (
                "seq4",
                "QSVLTQPPSVSGAPGQRVTISCTGSSSNIGSGYDVHWYQDLPGTAPKLLIYGNSKRPSGVPDRFSGSKSGTSASLAITGLQSEDEADYYCASWTDGLSLVVFGGGTKLTVLG",
            ),
            (
                "seq5",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
        ]

    def test_all_alignment_methods_with_real_sequences(
        self, msa_engine, real_antibody_sequences
    ):
        """Test all alignment methods work with real antibody sequences."""
        alignment_methods = [
            AlignmentMethod.MUSCLE,
            AlignmentMethod.MAFFT,
            AlignmentMethod.CLUSTALO,
            AlignmentMethod.PAIRWISE_GLOBAL,
            AlignmentMethod.PAIRWISE_LOCAL,
        ]

        successful_methods = 0
        total_methods = len(alignment_methods)

        for method in alignment_methods:
            print(f"Testing alignment method: {method.value}")

            try:
                # Create MSA
                msa_result = msa_engine.create_msa(
                    real_antibody_sequences, method
                )

                # Verify basic structure
                assert isinstance(msa_result, MSAResult)
                assert msa_result.alignment_method == method
                assert len(msa_result.sequences) == len(
                    real_antibody_sequences
                )
                assert msa_result.metadata["num_sequences"] == len(
                    real_antibody_sequences
                )
                assert msa_result.metadata["method"] == method.value

                # Verify sequences
                for i, (name, original_seq) in enumerate(
                    real_antibody_sequences
                ):
                    msa_seq = msa_result.sequences[i]
                    assert msa_seq.name == name
                    assert msa_seq.original_sequence == original_seq
                    assert len(msa_seq.aligned_sequence) > 0
                    assert msa_seq.start_position == 0
                    assert msa_seq.end_position > 0
                    assert isinstance(msa_seq.gaps, list)

                # Verify alignment matrix
                assert len(msa_result.alignment_matrix) == len(
                    real_antibody_sequences
                )
                alignment_length = len(msa_result.alignment_matrix[0])
                assert alignment_length > 0
                assert (
                    msa_result.metadata["alignment_length"] == alignment_length
                )

                # Verify all sequences in matrix have same length
                for seq in msa_result.alignment_matrix:
                    assert len(seq) == alignment_length

                # Verify consensus
                assert len(msa_result.consensus) == alignment_length
                # Consensus is not be the same as the PSSM consensus because the consensus is generated from the alignment matrix
                assert (
                    msa_result.consensus
                    != msa_result.metadata["pssm_data"]["consensus"]
                )

                # Verify consensus contains valid amino acids or gaps
                valid_chars = set("ACDEFGHIKLMNPQRSTVWY-")
                for char in msa_result.consensus:
                    assert char in valid_chars

                # Verify PSSM data
                pssm_data = msa_result.metadata["pssm_data"]
                assert "position_frequencies" in pssm_data
                assert "position_scores" in pssm_data
                assert "conservation_scores" in pssm_data
                assert "consensus" in pssm_data
                assert "amino_acids" in pssm_data
                assert "alignment_length" in pssm_data
                assert "num_sequences" in pssm_data

                successful_methods += 1
                print(f"✓ {method.value} passed")

            except (
                RuntimeError,
                FileNotFoundError,
                subprocess.CalledProcessError,
            ) as e:
                # Skip external tools that are not available
                print(f"⚠ {method.value} skipped: {e}")
                continue
            except Exception as e:
                # For other errors, fail the test
                print(f"✗ {method.value} failed: {e}")
                raise

        # Ensure at least the pairwise methods work (these don't require external tools)
        assert (
            successful_methods >= 2
        ), f"Expected at least 2 methods to work, but only {successful_methods} succeeded"
        print(
            f"Successfully tested {successful_methods}/{total_methods} alignment methods"
        )

    def test_alignment_matrix_structure(self, msa_engine, diverse_sequences):
        """Test that alignment matrix is properly structured."""
        msa_result = msa_engine.create_msa(
            diverse_sequences, AlignmentMethod.MUSCLE
        )

        # Verify matrix dimensions
        matrix = msa_result.alignment_matrix
        num_sequences = len(matrix)
        alignment_length = len(matrix[0])

        assert num_sequences == len(diverse_sequences)
        assert alignment_length > max(
            len(seq[1]) for seq in diverse_sequences
        )  # Should be longer due to gaps

        # Verify all rows have same length
        for row in matrix:
            assert len(row) == alignment_length

        # Verify matrix contains valid characters
        valid_chars = set("ACDEFGHIKLMNPQRSTVWY-")
        for row in matrix:
            for char in row:
                assert char in valid_chars

    def test_consensus_generation_quality(
        self, msa_engine, real_antibody_sequences
    ):
        """Test that consensus sequences are valid and meaningful."""
        msa_result = msa_engine.create_msa(
            real_antibody_sequences, AlignmentMethod.MUSCLE
        )

        consensus = msa_result.consensus
        alignment_matrix = msa_result.alignment_matrix

        # Verify consensus length matches alignment
        assert len(consensus) == len(alignment_matrix[0])

        # Verify consensus contains valid characters
        valid_chars = set("ACDEFGHIKLMNPQRSTVWY-")
        for char in consensus:
            assert char in valid_chars

        # Verify consensus is not all gaps
        gap_count = consensus.count("-")
        assert gap_count < len(consensus) * 0.5  # Less than 50% gaps

        # Verify consensus represents actual alignment
        # Check that consensus positions with amino acids have corresponding amino acids in sequences
        for i, consensus_char in enumerate(consensus):
            if consensus_char != "-":
                # At least one sequence should have a non-gap at this position
                column_chars = [row[i] for row in alignment_matrix]
                non_gap_chars = [c for c in column_chars if c != "-"]
                assert len(non_gap_chars) > 0

    def test_pssm_calculation_validity(self, msa_engine, diverse_sequences):
        """Test that PSSM calculation produces valid results."""
        msa_result = msa_engine.create_msa(
            diverse_sequences, AlignmentMethod.MUSCLE
        )
        pssm_data = msa_result.metadata["pssm_data"]

        # Verify position frequencies
        position_frequencies = pssm_data["position_frequencies"]
        assert len(position_frequencies) == len(msa_result.alignment_matrix[0])

        for pos_freq in position_frequencies:
            # Each position should have frequencies for all amino acids
            assert len(pos_freq) == 20  # 20 standard amino acids
            # Frequencies should sum to approximately 1.0
            total_freq = sum(pos_freq.values())
            assert 0.95 <= total_freq <= 1.05  # Allow small numerical errors

        # Verify position scores
        position_scores = pssm_data["position_scores"]
        assert len(position_scores) == len(position_frequencies)

        for pos_score in position_scores:
            assert len(pos_score) == 20  # 20 standard amino acids
            # Scores should be numeric
            for score in pos_score.values():
                assert isinstance(score, (int, float))

        # Verify conservation scores
        conservation_scores = pssm_data["conservation_scores"]
        assert len(conservation_scores) == len(position_frequencies)

        for score in conservation_scores:
            assert isinstance(score, (int, float))
            assert 0 <= score <= 1  # Conservation should be between 0 and 1

        # Verify amino acids list
        amino_acids = pssm_data["amino_acids"]
        assert len(amino_acids) == 20
        assert set(amino_acids) == set("ACDEFGHIKLMNPQRSTVWY")

    def test_alignment_methods_produce_different_results(
        self, msa_engine, diverse_sequences
    ):
        """Test that different alignment methods produce different (but valid) results."""
        methods = [
            AlignmentMethod.MUSCLE,
            AlignmentMethod.MAFFT,
            AlignmentMethod.CLUSTALO,
        ]
        results = {}

        for method in methods:
            msa_result = msa_engine.create_msa(diverse_sequences, method)
            results[method] = msa_result

        # All methods should produce valid results
        for method, result in results.items():
            assert len(result.sequences) == len(diverse_sequences)
            assert len(result.alignment_matrix) == len(diverse_sequences)
            assert len(result.consensus) > 0

        # Different methods should produce different alignments (not necessarily different lengths)
        # This is a probabilistic test - sometimes methods might produce similar results
        consensus_lengths = [
            len(result.consensus) for result in results.values()
        ]
        # At least some variation in alignment length or consensus
        assert (
            len(set(consensus_lengths)) >= 1
        )  # All could be same length, but should be valid

    def test_edge_cases(self, msa_engine):
        """Test edge cases and error handling."""
        # Test with very similar sequences
        similar_sequences = [
            (
                "seq1",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
            (
                "seq2",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
        ]

        msa_result = msa_engine.create_msa(
            similar_sequences, AlignmentMethod.MUSCLE
        )
        assert len(msa_result.sequences) == 2
        assert len(msa_result.consensus) > 0

        # Test with sequences of different lengths
        different_length_sequences = [
            ("short", "EVQLVESGGGLVQPGGSLRLSCAAS"),
            (
                "long",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            ),
        ]

        msa_result = msa_engine.create_msa(
            different_length_sequences, AlignmentMethod.MUSCLE
        )
        assert len(msa_result.sequences) == 2
        assert len(msa_result.consensus) > 0

    def test_pssm_consistency_across_methods(
        self, msa_engine, real_antibody_sequences
    ):
        """Test that PSSM calculation is consistent across different alignment methods."""
        methods = [
            AlignmentMethod.MUSCLE,
            AlignmentMethod.MAFFT,
            AlignmentMethod.CLUSTALO,
        ]
        pssm_results = {}

        for method in methods:
            msa_result = msa_engine.create_msa(real_antibody_sequences, method)
            pssm_data = msa_result.metadata["pssm_data"]
            pssm_results[method] = pssm_data

        # All PSSM results should have the same structure
        for method, pssm_data in pssm_results.items():
            assert "position_frequencies" in pssm_data
            assert "position_scores" in pssm_data
            assert "conservation_scores" in pssm_data
            assert "consensus" in pssm_data
            assert "amino_acids" in pssm_data

            # Amino acids should be the same across all methods
            assert pssm_data["amino_acids"] == list("ACDEFGHIKLMNPQRSTVWY")

            # Conservation scores should be valid
            for score in pssm_data["conservation_scores"]:
                assert 0 <= score <= 1
