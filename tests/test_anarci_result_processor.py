import pytest
from app.annotation.AnarciResultProcessor import AnarciResultProcessor
from app.annotation.AntibodyRegionAnnotator import AntibodyRegionAnnotator


@pytest.mark.parametrize("seq_dict_name,expected_domains", [
    ("scfv", 2),
    ("ighg1", 2),
    ("kih", 4),
    ("tcr", 1),
])
def test_anarci_result_processor_domains(seq_dict_name, expected_domains, SCFV_SEQ, IGHG1_SEQ, KIH_SEQ, TCR_SEQ):
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
    total_domains = sum(len(chain.domains) for chain in result_obj.chains)
    assert total_domains == expected_domains
    annotator = AntibodyRegionAnnotator()
    for chain in result_obj.chains:
        for domain in chain.domains:
            print(domain)
