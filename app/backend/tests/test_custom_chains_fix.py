"""
Test to verify that using custom_chains preserves the original FASTA header names.
"""

from backend.annotation.annotation_engine import (
    annotate_sequences_with_processor,
)
from backend.models.models import SequenceInput, NumberingScheme


def test_custom_chains_preserve_names():
    """Test that custom_chains preserves original FASTA header names."""

    # This simulates the NEW frontend approach using custom_chains
    sequence_inputs = [
        SequenceInput(
            name="Heavy_Chain_Patient_A",
            custom_chains={
                "Heavy_Chain_Patient_A": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            },
        ),
        SequenceInput(
            name="Light_Chain_Patient_B",
            custom_chains={
                "Light_Chain_Patient_B": "DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK"
            },
        ),
    ]

    print(f"\n1. Input sequence names:")
    for seq in sequence_inputs:
        print(f"   - {seq.name}")
        print(
            f"     custom_chains: {list(seq.custom_chains.keys()) if seq.custom_chains else 'None'}"
        )

    # Run annotation
    result = annotate_sequences_with_processor(
        sequence_inputs, NumberingScheme.IMGT
    )

    print(f"\n2. Annotation results:")
    print(f"   Total sequences: {len(result.sequences)}")

    returned_names = []
    for i, seq in enumerate(result.sequences):
        print(f"\n   Sequence {i + 1}:")
        print(f"     name: {seq.name}")
        print(f"     chain_type: {seq.chain_type}")
        returned_names.append(seq.name)

    # The key test - names should match the FASTA headers, not generic chain names
    expected_names = ["Heavy_Chain_Patient_A", "Light_Chain_Patient_B"]

    print(f"\n3. Name verification:")
    print(f"   Expected: {expected_names}")
    print(f"   Returned: {returned_names}")

    for expected_name in expected_names:
        assert (
            expected_name in returned_names
        ), f"Expected name '{expected_name}' not found in {returned_names}"

    # Also verify we don't get generic names
    generic_names = ["heavy_chain", "light_chain", "custom_chains"]
    for generic_name in generic_names:
        assert (
            generic_name not in returned_names
        ), f"Found generic name '{generic_name}' in results - names not preserved!"

    print(f"\n✅ All custom chain names preserved successfully!")


if __name__ == "__main__":
    test_custom_chains_preserve_names()
