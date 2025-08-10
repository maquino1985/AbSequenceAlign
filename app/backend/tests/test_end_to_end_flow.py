"""
End-to-end test to verify the complete flow from FASTA input to annotation result.
"""

from backend.annotation.annotation_engine import (
    annotate_sequences_with_processor,
)
from backend.annotation.sequence_processor import SequenceProcessor
from backend.models.models import (
    SequenceInput,
    NumberingScheme,
)


def test_fasta_to_annotation_flow():
    """Test the complete flow from FASTA string to annotation result."""

    # Simulate FASTA input like what comes from the frontend
    fasta_content = """>Heavy_Chain_Patient_A
EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK
>Light_Chain_Patient_A  
DIQMTQSPSSLSASVGDRVTITCRASQGIRNYLAWYQQKPGKAPKLLIYAASTLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQRYNRAPYTFGQGTKVEIK"""

    print(f"\n1. Original FASTA content:")
    print(fasta_content)

    # Parse FASTA like the frontend would
    sequence_processor = SequenceProcessor()
    records = sequence_processor.parse_fasta(fasta_content)

    print(f"\n2. Parsed FASTA records:")
    for record in records:
        print(f"   ID: {record.id}, Description: {record.description}")
        print(f"   Sequence: {str(record.seq)[:50]}...")

    # Convert to SequenceInput objects like the frontend would
    sequence_inputs = []
    for i, record in enumerate(records):
        # This simulates how the frontend creates SequenceInput objects
        sequence_input = SequenceInput(
            name=record.id,  # This should preserve the FASTA header
            heavy_chain=(
                str(record.seq) if "heavy" in record.id.lower() else None
            ),
            light_chain=(
                str(record.seq) if "light" in record.id.lower() else None
            ),
        )
        sequence_inputs.append(sequence_input)
        print(f"\n3. SequenceInput {i + 1}:")
        print(f"   name: {sequence_input.name}")
        print(
            f"   heavy_chain: {'Yes' if sequence_input.heavy_chain else 'No'}"
        )
        print(
            f"   light_chain: {'Yes' if sequence_input.light_chain else 'No'}"
        )

    # Run annotation
    result = annotate_sequences_with_processor(
        sequence_inputs, NumberingScheme.IMGT
    )

    print(f"\n4. Annotation results:")
    print(f"   Total sequences: {len(result.sequences)}")

    for i, seq in enumerate(result.sequences):
        print(f"\n   Sequence {i + 1}:")
        print(f"     name: {seq.name}")
        print(f"     chain_type: {seq.chain_type}")
        print(f"     sequence length: {len(seq.sequence)}")
        print(
            f"     regions: {list(seq.regions.keys()) if seq.regions else 'None'}"
        )

    # Verify that names are preserved
    original_names = [record.id for record in records]
    returned_names = [seq.name for seq in result.sequences]

    print(f"\n5. Name preservation check:")
    print(f"   Original names: {original_names}")
    print(f"   Returned names: {returned_names}")

    # The key assertion - names should be preserved
    for original_name in original_names:
        assert (
            original_name in returned_names
        ), f"Original name '{original_name}' not found in returned names {returned_names}"

    print(f"\n✅ All names preserved successfully!")


if __name__ == "__main__":
    test_fasta_to_annotation_flow()
