"""
Detailed test to trace exactly what happens to chain names through the annotation pipeline.
"""

import pytest
from backend.annotation.annotation_engine import annotate_sequences_with_processor
from backend.annotation.AnarciResultProcessor import AnarciResultProcessor
from backend.models.models import SequenceInput, NumberingScheme


def test_trace_chain_name_processing():
    """Trace what happens to chain names through the entire pipeline."""
    
    # Create test input with specific name
    sequence_input = SequenceInput(
        name="My_Custom_Heavy_Chain_Name",
        heavy_chain="EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
    )
    
    print(f"\n1. Original SequenceInput name: {sequence_input.name}")
    
    # Check what get_all_chains() returns
    chains_dict = sequence_input.get_all_chains()
    print(f"2. get_all_chains() returns: {list(chains_dict.keys())}")
    
    # Create the input dict that goes to AnarciResultProcessor
    input_dict = {}
    for seq in [sequence_input]:
        chain_data = seq.get_all_chains()
        if chain_data:
            input_dict[seq.name] = chain_data
    
    print(f"3. Input dict to AnarciResultProcessor: {input_dict}")
    
    # Create processor and check results
    processor = AnarciResultProcessor(input_dict, numbering_scheme="imgt")
    
    print(f"4. AnarciResultProcessor results:")
    for result_obj in processor.results:
        print(f"   - biologic_name: {result_obj.biologic_name}")
        for chain in result_obj.chains:
            print(f"   - chain.name: {chain.name}")
    
    # Now run through annotation engine
    result = annotate_sequences_with_processor([sequence_input], NumberingScheme.IMGT)
    
    print(f"5. Final annotation result:")
    for seq in result.sequences:
        print(f"   - sequence.name: {seq.name}")
        print(f"   - sequence.chain_type: {seq.chain_type}")
    
    # The assertion
    assert len(result.sequences) >= 1
    first_sequence = result.sequences[0]
    
    print(f"\n6. ASSERTION: Expected 'My_Custom_Heavy_Chain_Name', got '{first_sequence.name}'")
    
    # This should pass if the fix is working
    assert first_sequence.name == "My_Custom_Heavy_Chain_Name", f"Chain name not preserved! Expected 'My_Custom_Heavy_Chain_Name', got '{first_sequence.name}'"


if __name__ == "__main__":
    test_trace_chain_name_processing()
