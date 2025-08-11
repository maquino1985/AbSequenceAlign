#!/usr/bin/env python3

import sys

sys.path.append("/Users/aquinmx3/repos/AbSequenceAlign/app")

from backend.annotation.anarci_result_processor import AnarciResultProcessor


def test_scfv_annotation() -> None:
    """Test scFv annotation directly"""
    scfv_sequence = "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"

    seq_dict = {"test_scfv": {"scfv_chain": scfv_sequence}}

    print(f"Testing scFv sequence: {scfv_sequence[:50]}...")
    print(f"Sequence length: {len(scfv_sequence)}")

    processor = AnarciResultProcessor(seq_dict, numbering_scheme="imgt")
    result = processor.get_result_by_biologic_name("test_scfv")

    if result is None:
        print("ERROR: No result returned")
        return

    print(f"Number of chains: {len(result.chains)}")

    for i, chain in enumerate(result.chains):
        print(f"\nChain {i}: {chain.name}")
        print(f"Number of domains: {len(chain.domains)}")

        for j, domain in enumerate(chain.domains):
            print(f"  Domain {j}: {domain.domain_type}")
            print(f"    Sequence: {domain.sequence[:50]}...")
            print(f"    Length: {len(domain.sequence)}")

            if hasattr(domain, "regions") and domain.regions:
                print(f"    Regions: {domain.regions}")
                print(f"    Regions type: {type(domain.regions)}")
                print(f"    Regions keys: {list(domain.regions.keys())}")
                print(f"    Regions values: {list(domain.regions.values())}")
                if domain.regions:
                    first_key = list(domain.regions.keys())[0]
                    print(
                        f"    First region data: {domain.regions[first_key]}"
                    )
            else:
                print(f"    Regions: None")
                print(f"    Has regions attr: {hasattr(domain, 'regions')}")


if __name__ == "__main__":
    test_scfv_annotation()
