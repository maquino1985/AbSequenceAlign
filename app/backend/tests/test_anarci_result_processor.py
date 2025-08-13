import pytest
from backend.annotation.anarci_result_processor import AnarciResultProcessor
from backend.logger import logger


@pytest.mark.parametrize(
    "seq_dict_name,expected_v_domains,expected_c_domains",
    [
        ("scfv", 2, 0),  # scFv has 2 variable domains, no constant
        ("ighg1", 2, 2),  # IgG1 has 2 variable domains and 2 constant regions
        ("kih", 4, 4),  # KiH has 4 variable domains and 4 constant regions
        ("tcr", 1, 0),  # TCR has 1 variable domain in this test
    ],
)
def test_anarci_result_processor_domains(
    seq_dict_name,
    expected_v_domains,
    expected_c_domains,
    SCFV_SEQ,
    IGHG1_SEQ,
    KIH_SEQ,
    TCR_SEQ,
):
    seq_dicts = {
        "scfv": SCFV_SEQ,
        "ighg1": IGHG1_SEQ,
        "kih": KIH_SEQ,
        "tcr": TCR_SEQ,
    }
    seq_dict = {seq_dict_name: seq_dicts[seq_dict_name]}
    scheme = "kabat"
    processor = AnarciResultProcessor(seq_dict, numbering_scheme=scheme)
    biologic_name = next(iter(seq_dict.keys()))
    result_obj = processor.get_result_by_biologic_name(biologic_name)

    assert result_obj is not None

    # Count variable and constant domains
    v_domains = []
    c_domains = []
    for chain in result_obj.chains:
        for domain in chain.domains:
            if domain.domain_type == "V":
                v_domains.append(domain)
            elif domain.domain_type == "C":
                c_domains.append(domain)

    assert (
        len(v_domains) == expected_v_domains
    ), f"Expected {expected_v_domains} variable domains, got {len(v_domains)}"
    assert (
        len(c_domains) == expected_c_domains
    ), f"Expected {expected_c_domains} constant domains, got {len(c_domains)}"

    # Print domain details for debugging
    for chain in result_obj.chains:
        logger.info(f"\nChain: {chain.name}")
        for domain in chain.domains:
            logger.info(f"  Domain type: {domain.domain_type}")
            if domain.domain_type == "C" and domain.constant_region_info:
                logger.info(
                    f"    Isotype: {domain.constant_region_info['isotype']}"
                )
                logger.info(
                    f"    Position: {domain.constant_region_info['start']}-{domain.constant_region_info['end']}"
                )


def test_constant_region_detection(IGHG1_SEQ):
    """Test specific constant region detection functionality"""
    # Use IgG1 sequence which has known constant regions
    seq_dict = {"test_antibody": {"heavy_chain": IGHG1_SEQ["heavy_chain"]}}

    processor = AnarciResultProcessor(seq_dict, numbering_scheme="cgg")
    result = processor.get_result_by_biologic_name("test_antibody")

    assert result is not None
    assert len(result.chains) == 1

    chain = result.chains[0]
    constant_domains = [d for d in chain.domains if d.domain_type == "C"]

    assert (
        len(constant_domains) == 1
    ), "Expected 1 constant domain for IgG1 heavy chain"

    c_domain = constant_domains[0]
    assert c_domain.constant_region_info is not None
    assert c_domain.constant_region_info["isotype"] == "IGHG1"
    assert c_domain.constant_region_info["domain_type"] == "C"
    assert isinstance(c_domain.constant_region_info["start"], int)
    assert isinstance(c_domain.constant_region_info["end"], int)
    assert c_domain.constant_region_info["start"] > 0
    assert (
        c_domain.constant_region_info["end"]
        > c_domain.constant_region_info["start"]
    )


def test_scfv_sequence_positions():
    """
    Test that scFv sequence regions have correct positions.
    
    This test verifies the exact positions for all regions in the scFv sequence:
    - First variable domain (positions 1-107)
    - Linker (positions 108-128) 
    - Second variable domain (positions 129-247)
    
    Expected regions and positions based on user analysis:
    First Variable Domain:
    - FR1: 1-23
    - CDR1: 24-34  
    - FR2: 35-49
    - CDR2: 50-56
    - FR3: 57-88
    - CDR3: 89-97
    - FR4: 98-107
    
    Linker: 108-128
    
    Second Variable Domain:
    - FR1: 129-153
    - CDR1: 154-163
    - FR2: 164-177
    - CDR2: 178-194 (should include the last G)
    - FR3: 195-226
    - CDR3: 227-236
    - FR4: 237-247
    """
    # Arrange: Define the scFv sequence with correct concatenation
    scfv_sequence = (
        "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
        "GGGGGSGGGGSGGGGSGGGGS"
        "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
    )
    
    seq_dict = {"scfv_test": {"scfv_chain": scfv_sequence}}
    
    # Act: Process the sequence
    processor = AnarciResultProcessor(seq_dict, numbering_scheme="cgg")
    result_obj = processor.get_result_by_biologic_name("scfv_test")
    
    # Assert: Verify basic structure
    assert result_obj is not None, "Result object should not be None"
    assert len(result_obj.chains) == 1, "Should have exactly 1 chain"
    
    chain = result_obj.chains[0]
    assert chain.name == "scfv_chain", "Chain name should be 'scfv_chain'"
    
    # Get all domains and regions
    domains = chain.domains
    assert len(domains) >= 3, f"Should have at least 3 domains (2 variable + linker), got {len(domains)}"
    
    # Find variable domains and linker
    variable_domains = [d for d in domains if d.domain_type == "V"]
    linker_domains = [d for d in domains if d.domain_type == "LINKER"]
    
    assert len(variable_domains) == 2, f"Should have exactly 2 variable domains, got {len(variable_domains)}"
    assert len(linker_domains) == 1, f"Should have exactly 1 linker domain, got {len(linker_domains)}"
    
    # Test first variable domain regions
    first_v_domain = variable_domains[0]
    assert first_v_domain.regions is not None, "First variable domain should have regions"
    
    # Expected positions for first variable domain
    expected_first_domain = {
        "FR1": (1, 23),
        "CDR1": (24, 34),
        "FR2": (35, 49),
        "CDR2": (50, 56),
        "FR3": (57, 88),
        "CDR3": (89, 97),
        "FR4": (98, 107)
    }
    
    for region_name, (expected_start, expected_stop) in expected_first_domain.items():
        region = next((r for r in first_v_domain.regions if r.name == region_name), None)
        assert region is not None, f"Region {region_name} should exist in first variable domain"
        assert region.start == expected_start, f"Region {region_name} should start at {expected_start}, got {region.start}"
        assert region.stop == expected_stop, f"Region {region_name} should stop at {expected_stop}, got {region.stop}"
    
    # Test linker domain
    linker_domain = linker_domains[0]
    assert linker_domain.regions is not None, "Linker domain should have regions"
    assert len(linker_domain.regions) == 1, "Linker domain should have exactly 1 region"
    
    linker_region = linker_domain.regions[0]
    assert linker_region.name == "LINKER", "Linker region should be named 'LINKER'"
    assert linker_region.start == 108, f"Linker should start at 108, got {linker_region.start}"
    assert linker_region.stop == 128, f"Linker should stop at 128, got {linker_region.stop}"
    assert len(linker_region.sequence) == 21, f"Linker should be 21 residues long, got {len(linker_region.sequence)}"
    
    # Test second variable domain regions
    second_v_domain = variable_domains[1]
    assert second_v_domain.regions is not None, "Second variable domain should have regions"
    
    # Expected positions for second variable domain (corrected based on user analysis)
    expected_second_domain = {
        "FR1": (129, 153),
        "CDR1": (154, 163),
        "FR2": (164, 177),
        "CDR2": (178, 194),
        "FR3": (195, 226),
        "CDR3": (227, 236),
        "FR4": (237, 247)
    }
    
    for region_name, (expected_start, expected_stop) in expected_second_domain.items():
        region = next((r for r in second_v_domain.regions if r.name == region_name), None)
        assert region is not None, f"Region {region_name} should exist in second variable domain"
        assert region.start == expected_start, f"Region {region_name} should start at {expected_start}, got {region.start}"
        assert region.stop == expected_stop, f"Region {region_name} should stop at {expected_stop}, got {region.stop}"
    
    # Additional assertions for specific problematic regions
    cdr2_second = next((r for r in second_v_domain.regions if r.name == "CDR2"), None)
    if cdr2_second:
        assert cdr2_second.stop == 194, f"Second CDR2 should end at 194, got {cdr2_second.stop}"
        # Verify the sequence ends with 'G' at position 194
        expected_cdr2_seq = scfv_sequence[cdr2_second.start-1:cdr2_second.stop]
        assert expected_cdr2_seq.endswith('G'), f"CDR2 sequence should end with 'G', got '{expected_cdr2_seq[-1]}'"
    
    cdr3_second = next((r for r in second_v_domain.regions if r.name == "CDR3"), None)
    if cdr3_second:
        assert cdr3_second.start == 227, f"Second CDR3 should start at 227, got {cdr3_second.start}"
        assert cdr3_second.stop == 236, f"Second CDR3 should stop at 234, got {cdr3_second.stop}"
    
    fr4_second = next((r for r in second_v_domain.regions if r.name == "FR4"), None)
    if fr4_second:
        assert fr4_second.start == 237, f"Second FR4 should start at 237, got {fr4_second.start}"
        assert fr4_second.stop == 247, f"Second FR4 should stop at 247, got {fr4_second.stop}"


def test_scfv_chain_preservation(SCFV_SEQ):
    """Test that scFv remains as one chain with multiple domains"""
    seq_dict = {"scfv": SCFV_SEQ}

    processor = AnarciResultProcessor(seq_dict, numbering_scheme="cgg")
    result = processor.get_result_by_biologic_name("scfv")

    assert result is not None
    assert (
        len(result.chains) == 1
    ), "scFv should be processed as a single chain"

    chain = result.chains[0]
    assert (
        len(chain.domains) == 3
    ), "scFv should have 2 variable domains and 1 linker domain"

    # Verify domain order and linker detection
    domains = chain.domains
    assert domains[0].domain_type == "V"
    assert domains[1].domain_type == "LINKER"
    assert domains[2].domain_type == "V"

    # Check for linker information
    linker_domain = domains[1]
    assert linker_domain.domain_type == "LINKER"
    assert (
        linker_domain.sequence.count("G") > 0
    ), "Linker should contain glycine residues"
    """
    Test that scFv sequence regions have correct positions.
    
    This test verifies the exact positions for all regions in the scFv sequence:
    - First variable domain (positions 1-107)
    - Linker (positions 108-128) 
    - Second variable domain (positions 129-247)
    
    Expected regions and positions based on user analysis:
    First Variable Domain:
    - FR1: 1-23
    - CDR1: 24-34  
    - FR2: 35-49
    - CDR2: 50-56
    - FR3: 57-88
    - CDR3: 89-97
    - FR4: 98-107
    
    Linker: 108-128
    
    Second Variable Domain:
    - FR1: 129-151
    - CDR1: 152-162
    - FR2: 163-177
    - CDR2: 178-194 (should include the last G)
    - FR3: 195-226
    - CDR3: 227-234
    - FR4: 237-247
    """
    # Arrange: Define the scFv sequence with correct concatenation
    scfv_sequence = (
        "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
        "GGGGGSGGGGSGGGGSGGGGS"
        "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
    )
    
    seq_dict = {"scfv_test": {"scfv_chain": scfv_sequence}}
    
    # Act: Process the sequence
    processor = AnarciResultProcessor(seq_dict, numbering_scheme="cgg")
    result_obj = processor.get_result_by_biologic_name("scfv_test")
    
    # Assert: Verify basic structure
    assert result_obj is not None, "Result object should not be None"
    assert len(result_obj.chains) == 1, "Should have exactly 1 chain"
    
    chain = result_obj.chains[0]
    assert chain.name == "scfv_chain", "Chain name should be 'scfv_chain'"
    
    # Get all domains and regions
    domains = chain.domains
    assert len(domains) >= 3, f"Should have at least 3 domains (2 variable + linker), got {len(domains)}"
    
    # Find variable domains and linker
    variable_domains = [d for d in domains if d.domain_type == "V"]
    linker_domains = [d for d in domains if d.domain_type == "LINKER"]
    
    assert len(variable_domains) == 2, f"Should have exactly 2 variable domains, got {len(variable_domains)}"
    assert len(linker_domains) == 1, f"Should have exactly 1 linker domain, got {len(linker_domains)}"
    
    # Test first variable domain regions
    first_v_domain = variable_domains[0]
    assert first_v_domain.regions is not None, "First variable domain should have regions"
    
    # Expected positions for first variable domain
    expected_first_domain = {
        "FR1": (1, 23),
        "CDR1": (24, 34),
        "FR2": (35, 49),
        "CDR2": (50, 56),
        "FR3": (57, 88),
        "CDR3": (89, 97),
        "FR4": (98, 107)
    }
    
    for region_name, (expected_start, expected_stop) in expected_first_domain.items():
        region = next((r for r in first_v_domain.regions if r.name == region_name), None)
        assert region is not None, f"Region {region_name} should exist in first variable domain"
        assert region.start == expected_start, f"Region {region_name} should start at {expected_start}, got {region.start}"
        assert region.stop == expected_stop, f"Region {region_name} should stop at {expected_stop}, got {region.stop}"
    
    # Test linker domain
    linker_domain = linker_domains[0]
    assert linker_domain.regions is not None, "Linker domain should have regions"
    assert len(linker_domain.regions) == 1, "Linker domain should have exactly 1 region"
    
    linker_region = linker_domain.regions[0]
    assert linker_region.name == "LINKER", "Linker region should be named 'LINKER'"
    assert linker_region.start == 108, f"Linker should start at 108, got {linker_region.start}"
    assert linker_region.stop == 128, f"Linker should stop at 128, got {linker_region.stop}"
    assert len(linker_region.sequence) == 21, f"Linker should be 21 residues long, got {len(linker_region.sequence)}"
    
    # Test second variable domain regions
    second_v_domain = variable_domains[1]
    assert second_v_domain.regions is not None, "Second variable domain should have regions"
    
    # Expected positions for second variable domain (corrected based on user analysis)
    expected_second_domain = {
        "FR1": (129, 151),
        "CDR1": (152, 162),
        "FR2": (163, 177),
        "CDR2": (178, 194),  # Should include the last G
        "FR3": (195, 226),
        "CDR3": (227, 234),  # Should be 227-234, not 223-230
        "FR4": (237, 247)    # Should be 237-247, not 231-241
    }
    
    for region_name, (expected_start, expected_stop) in expected_second_domain.items():
        region = next((r for r in second_v_domain.regions if r.name == region_name), None)
        assert region is not None, f"Region {region_name} should exist in second variable domain"
        assert region.start == expected_start, f"Region {region_name} should start at {expected_start}, got {region.start}"
        assert region.stop == expected_stop, f"Region {region_name} should stop at {expected_stop}, got {region.stop}"
    
    # Additional assertions for specific problematic regions
    cdr2_second = next((r for r in second_v_domain.regions if r.name == "CDR2"), None)
    if cdr2_second:
        assert cdr2_second.stop == 194, f"Second CDR2 should end at 194, got {cdr2_second.stop}"
        # Verify the sequence ends with 'G' at position 194
        expected_cdr2_seq = scfv_sequence[cdr2_second.start-1:cdr2_second.stop]
        assert expected_cdr2_seq.endswith('G'), f"CDR2 sequence should end with 'G', got '{expected_cdr2_seq[-1]}'"
    
    cdr3_second = next((r for r in second_v_domain.regions if r.name == "CDR3"), None)
    if cdr3_second:
        assert cdr3_second.start == 227, f"Second CDR3 should start at 227, got {cdr3_second.start}"
        assert cdr3_second.stop == 234, f"Second CDR3 should stop at 234, got {cdr3_second.stop}"
    
    fr4_second = next((r for r in second_v_domain.regions if r.name == "FR4"), None)
    if fr4_second:
        assert fr4_second.start == 237, f"Second FR4 should start at 237, got {fr4_second.start}"
        assert fr4_second.stop == 247, f"Second FR4 should stop at 247, got {fr4_second.stop}"


def test_domain_boundary_calculations():
    """
    Test to analyze domain boundary calculations and identify position calculation issues.
    This test examines the raw ANARCI output and domain boundary detection.
    """
    # Define the scFv sequence
    scfv_sequence = (
        "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIK"
        "GGGGGSGGGGSGGGGSGGGGS"
        "QVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
    )
    
    seq_dict = {"scfv_test": {"scfv_chain": scfv_sequence}}
    
    # Process the sequence
    processor = AnarciResultProcessor(seq_dict, numbering_scheme="cgg")
    result_obj = processor.get_result_by_biologic_name("scfv_test")
    
    # Get all domains
    domains = result_obj.chains[0].domains
    variable_domains = [d for d in domains if d.domain_type == "V"]
    linker_domains = [d for d in domains if d.domain_type == "LINKER"]
    
    print(f"\n=== DOMAIN BOUNDARY ANALYSIS ===")
    print(f"Total domains: {len(domains)}")
    print(f"Variable domains: {len(variable_domains)}")
    print(f"Linker domains: {len(linker_domains)}")
    
    # Analyze first variable domain
    first_v_domain = variable_domains[0]
    print(f"\n=== FIRST VARIABLE DOMAIN ===")
    print(f"Domain sequence: {first_v_domain.sequence}")
    print(f"Domain length: {len(first_v_domain.sequence)}")
    print(f"Alignment details: {first_v_domain.alignment_details}")
    
    # Check if alignment_details has domain boundaries
    if hasattr(first_v_domain.alignment_details, 'get'):
        query_start = first_v_domain.alignment_details.get('query_start', 'N/A')
        query_end = first_v_domain.alignment_details.get('query_end', 'N/A')
        print(f"ANARCI query_start: {query_start}")
        print(f"ANARCI query_end: {query_end}")
    
    # Analyze linker domain
    if linker_domains:
        linker_domain = linker_domains[0]
        print(f"\n=== LINKER DOMAIN ===")
        print(f"Linker sequence: {linker_domain.sequence}")
        print(f"Linker length: {len(linker_domain.sequence)}")
        print(f"Linker alignment details: {linker_domain.alignment_details}")
        
        if hasattr(linker_domain.alignment_details, 'get'):
            linker_start = linker_domain.alignment_details.get('start', 'N/A')
            linker_end = linker_domain.alignment_details.get('end', 'N/A')
            print(f"Linker start: {linker_start}")
            print(f"Linker end: {linker_end}")
    
    # Analyze second variable domain
    second_v_domain = variable_domains[1]
    print(f"\n=== SECOND VARIABLE DOMAIN ===")
    print(f"Domain sequence: {second_v_domain.sequence}")
    print(f"Domain length: {len(second_v_domain.sequence)}")
    print(f"Alignment details: {second_v_domain.alignment_details}")
    
    if hasattr(second_v_domain.alignment_details, 'get'):
        query_start = second_v_domain.alignment_details.get('query_start', 'N/A')
        query_end = second_v_domain.alignment_details.get('query_end', 'N/A')
        print(f"ANARCI query_start: {query_start}")
        print(f"ANARCI query_end: {query_end}")
    
    # Analyze region positions within second domain
    print(f"\n=== SECOND DOMAIN REGIONS ===")
    for region in second_v_domain.regions:
        print(f"{region.name}: {region.start}-{region.stop} (length: {region.stop - region.start + 1})")
        print(f"  Sequence: {region.sequence}")
        print(f"  Expected sequence from domain: {second_v_domain.sequence[region.start - second_v_domain.alignment_details.get('query_start', 0) - 1:region.stop - second_v_domain.alignment_details.get('query_start', 0)]}")
    
    # Check the raw sequence positions
    print(f"\n=== SEQUENCE POSITION VERIFICATION ===")
    print(f"Full sequence length: {len(scfv_sequence)}")
    
    # Check where the second domain should start based on sequence
    first_domain_end = first_v_domain.alignment_details.get('query_end', 0)
    linker_length = len(linker_domain.sequence) if linker_domains else 0
    expected_second_start = first_domain_end + linker_length
    
    print(f"First domain end: {first_domain_end}")
    print(f"Linker length: {linker_length}")
    print(f"Expected second domain start: {expected_second_start}")
    print(f"Actual second domain start: {second_v_domain.alignment_details.get('query_start', 'N/A')}")
    
    # Verify the sequence at the expected positions
    if expected_second_start < len(scfv_sequence):
        actual_second_start = second_v_domain.alignment_details.get('query_start', 0)
        print(f"Sequence at expected start: {scfv_sequence[expected_second_start:expected_second_start+10]}")
        print(f"Sequence at actual start: {scfv_sequence[actual_second_start:actual_second_start+10]}")
    
    # Assertions to identify the specific issues
    assert len(variable_domains) == 2, "Should have exactly 2 variable domains"
    assert len(linker_domains) == 1, "Should have exactly 1 linker domain"
    
    # Check if the domain boundaries make sense
    first_end = first_v_domain.alignment_details.get('query_end', 0)
    linker_start = linker_domain.alignment_details.get('start', 0)
    linker_end = linker_domain.alignment_details.get('end', 0)
    second_start = second_v_domain.alignment_details.get('query_start', 0)
    
    print(f"\n=== BOUNDARY CONSISTENCY CHECK ===")
    print(f"First domain end: {first_end}")
    print(f"Linker start: {linker_start}")
    print(f"Linker end: {linker_end}")
    print(f"Second domain start: {second_start}")
    
    # Check for gaps or overlaps
    if first_end != linker_start:
        print(f"⚠️  GAP/OVERLAP: First domain ends at {first_end}, linker starts at {linker_start}")
    
    if linker_end != second_start:
        print(f"⚠️  GAP/OVERLAP: Linker ends at {linker_end}, second domain starts at {second_start}")
    
    # The test passes if we can identify the issues
    print(f"\n=== ANALYSIS COMPLETE ===")
