"""
Integration tests for annotation pipeline with real data.
Tests the full flow from request to response with minimal mocking.
"""

import pytest

from backend.models.models import SequenceInput, NumberingScheme
from backend.models.requests_v2 import AnnotationRequestV2
from backend.services.annotation_service import AnnotationService


class TestAnnotationIntegration:
    """Integration tests for the full annotation pipeline."""

    @pytest.fixture
    def real_antibody_sequences(self):
        """Real antibody sequences for testing."""
        return {
            "heavy_chain": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
            "light_chain": "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
        }

    @pytest.fixture
    def annotation_request(self, real_antibody_sequences):
        """Create a realistic annotation request."""
        return AnnotationRequestV2(
            sequences=[
                SequenceInput(
                    name="test_antibody",
                    heavy_chain=real_antibody_sequences["heavy_chain"],
                    light_chain=real_antibody_sequences["light_chain"],
                )
            ],
            numbering_scheme=NumberingScheme.IMGT,
        )

    def test_input_dict_preparation(self, annotation_request):
        """Test that input dictionary is correctly prepared from request."""
        service = AnnotationService()
        input_dict = service._prepare_input_dict(annotation_request)

        assert "test_antibody" in input_dict
        chains = input_dict["test_antibody"]
        assert "heavy_chain" in chains
        assert "light_chain" in chains
        assert len(chains["heavy_chain"]) > 100  # Realistic heavy chain length
        assert len(chains["light_chain"]) > 100  # Realistic light chain length

    def test_full_annotation_pipeline_with_real_data(self, IGHG1_SEQ):
        """Test the full annotation pipeline with real antibody sequences."""
        # Create annotation request with real data
        request = AnnotationRequestV2(
            sequences=[
                SequenceInput(
                    name="test_igg1_antibody",
                    heavy_chain=IGHG1_SEQ["heavy_chain"],
                    light_chain=IGHG1_SEQ["light_chain"],
                )
            ],
            numbering_scheme=NumberingScheme.IMGT,
        )

        # Run the actual annotation
        service = AnnotationService()
        result = service.process_annotation_request(request)

        # Verify basic result structure
        assert result.numbering_scheme == "imgt"
        assert result.total_sequences == 1
        assert len(result.sequences) == 1

        # Verify sequence structure
        sequence = result.sequences[0]
        assert sequence.name == "test_igg1_antibody"
        assert (
            len(sequence.chains) >= 1
        )  # At least one chain should be processed

        # Verify that chains have domains
        for chain in sequence.chains:
            assert len(chain.domains) >= 1
            assert chain.sequence is not None
            assert len(chain.sequence) > 0

        # Verify that domains have regions (if they're variable domains)
        for chain in sequence.chains:
            for domain in chain.domains:
                if domain.domain_type.value == "variable":
                    assert len(domain.regions) > 0
                    # Verify region structure
                    for region in domain.regions:
                        assert region.start > 0  # Should be 1-based
                        assert region.stop > region.start
                        assert len(region.features) > 0
                        assert region.features[0].kind == "sequence"

        # Verify statistics are calculated
        assert isinstance(result.chain_types, dict)
        assert isinstance(result.isotypes, dict)
        assert isinstance(result.species, dict)

    def test_scfv_annotation_pipeline(self, SCFV_SEQ):
        """Test annotation pipeline with scFv sequence."""
        request = AnnotationRequestV2(
            sequences=[
                SequenceInput(name="test_scfv", scfv=SCFV_SEQ["scfv_chain"])
            ],
            numbering_scheme=NumberingScheme.IMGT,
        )

        service = AnnotationService()
        result = service.process_annotation_request(request)

        assert result.numbering_scheme == "imgt"
        assert result.total_sequences == 1
        assert len(result.sequences) == 1

        sequence = result.sequences[0]
        assert sequence.name == "test_scfv"
        assert len(sequence.chains) >= 1

    def test_multiple_antibody_annotation(self, KIH_SEQ):
        """Test annotation pipeline with multiple antibodies (KIH format)."""
        request = AnnotationRequestV2(
            sequences=[
                SequenceInput(
                    name="kih_antibody_1",
                    heavy_chain_1=KIH_SEQ["heavy_chain_1"],
                    light_chain_1=KIH_SEQ["light_chain_1"],
                ),
                SequenceInput(
                    name="kih_antibody_2",
                    heavy_chain_2=KIH_SEQ["heavy_chain_2"],
                    light_chain_2=KIH_SEQ["light_chain_2"],
                ),
            ],
            numbering_scheme=NumberingScheme.IMGT,
        )

        service = AnnotationService()
        result = service.process_annotation_request(request)

        assert result.numbering_scheme == "imgt"
        assert result.total_sequences == 2
        assert len(result.sequences) == 2

        # Verify both sequences were processed
        for sequence in result.sequences:
            assert len(sequence.chains) >= 1
            for chain in sequence.chains:
                assert len(chain.domains) >= 1

    def test_multiple_sequences_statistics(self):
        """Test statistics calculation with multiple sequences."""
        request = AnnotationRequestV2(
            sequences=[
                SequenceInput(
                    name="seq1",
                    heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGMDVWGQGTTVTVSS",
                ),
                SequenceInput(
                    name="seq2",
                    heavy_chain="QVQLVQSGAEVKKPGASVKVSCKASGYTFTGYYMHWVRQAPGQGLEWMGWINPNSGGTNYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARATYYYGSRGYAMDYWGQGTLVTVSS",
                ),
            ],
            numbering_scheme=NumberingScheme.IMGT,
        )

        service = AnnotationService()
        input_dict = service._prepare_input_dict(request)

        assert len(input_dict) == 2
        assert "seq1" in input_dict
        assert "seq2" in input_dict
        assert all(
            len(chains["heavy_chain"]) > 100 for chains in input_dict.values()
        )

    def test_empty_sequences_handling(self):
        """Test handling of edge cases like empty sequences."""
        request = AnnotationRequestV2(
            sequences=[], numbering_scheme=NumberingScheme.IMGT
        )

        service = AnnotationService()
        input_dict = service._prepare_input_dict(request)
        assert len(input_dict) == 0
