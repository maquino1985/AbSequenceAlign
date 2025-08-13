"""
Test to ensure that chain names from frontend JSON payload are preserved in backend response.
"""

from backend.annotation.annotation_engine import (
    annotate_sequences_with_processor,
)
from backend.models.models import SequenceInput, NumberingScheme


def test_chain_name_preservation_single_sequence() -> None:
    """Test that a single sequence with custom name preserves the name."""

    # Example sequence with custom name
    sequence_input = SequenceInput(
        name="Custom_Heavy_Chain_VH1",
        heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK",
    )

    # Call annotation engine
    result = annotate_sequences_with_processor(
        [sequence_input], NumberingScheme.IMGT
    )

    # Verify that the returned sequence name matches the input name
    assert len(result.sequences) == 1
    returned_sequence = result.sequences[0]

    # This should be the original name, not "heavy_chain"
    assert (
        returned_sequence.name == "Custom_Heavy_Chain_VH1"
    ), f"Expected 'Custom_Heavy_Chain_VH1', got '{returned_sequence.name}'"


def test_chain_name_preservation_multiple_sequences() -> None:
    """Test that multiple sequences with custom names preserve their names."""

    sequence_inputs = [
        SequenceInput(
            name="Patient_A_Heavy_Chain",
            heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK",
        ),
        SequenceInput(
            name="Patient_B_Light_Chain",
            light_chain="DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC",
        ),
    ]

    # Call annotation engine
    result = annotate_sequences_with_processor(
        sequence_inputs, NumberingScheme.IMGT
    )

    # Verify that the returned sequence names match the input names
    assert len(result.sequences) == 2

    returned_names = [seq.name for seq in result.sequences]
    expected_names = ["Patient_A_Heavy_Chain", "Patient_B_Light_Chain"]

    for expected_name in expected_names:
        assert (
            expected_name in returned_names
        ), f"Expected '{expected_name}' in returned names {returned_names}"


def test_chain_name_preservation_with_custom_chains() -> None:
    """Test that custom chain names are preserved."""

    sequence_input = SequenceInput(
        name="Experiment_123",
        custom_chains={
            "VH_domain_only": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
            "VL_kappa_variant": "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK",
        },
    )

    # Call annotation engine
    result = annotate_sequences_with_processor(
        [sequence_input], NumberingScheme.IMGT
    )

    # Since we have custom chains, we should get results for each chain
    # But the sequence name should still be based on the main name
    assert len(result.sequences) >= 1

    # All sequences should be associated with the main sequence name
    for seq in result.sequences:
        assert (
            seq.name == "Experiment_123"
        ), f"Expected 'Experiment_123', got '{seq.name}'"


if __name__ == "__main__":
    # Run the tests
    test_chain_name_preservation_single_sequence()
    test_chain_name_preservation_multiple_sequences()
    test_chain_name_preservation_with_custom_chains()
    print("All chain name preservation tests passed!")
