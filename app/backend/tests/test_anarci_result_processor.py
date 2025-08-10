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

    processor = AnarciResultProcessor(seq_dict, numbering_scheme="imgt")
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


def test_scfv_chain_preservation(SCFV_SEQ):
    """Test that scFv remains as one chain with multiple domains"""
    seq_dict = {"scfv": SCFV_SEQ}

    processor = AnarciResultProcessor(seq_dict, numbering_scheme="imgt")
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
