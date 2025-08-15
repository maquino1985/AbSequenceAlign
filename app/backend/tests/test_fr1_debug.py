"""
Test to debug why FR1 is missing from CGG annotation.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from annotation.AnarciResultProcessor import AnarciResultProcessor
from annotation.AntibodyRegionAnnotator import AntibodyRegionAnnotator
from annotation.region_utils import RegionIndexHelper
from logger import logger


def test_fr1_missing_debug():
    """Debug why FR1 is missing from CGG annotation."""

    # Test sequence from the API response
    test_input = {
        "scfv": {
            "scfv": "DIVLTQSPATLSLSPGERATLSCRASQDVNTAVAWYQQKPDQSPKLLIYWASTRHTGVPARFTGSGSGTDYTLTISSLQPEDEAVYFCQQHHVSPWTFGGGTKVEIKGGGGGSGGGGSGGGGSGGGGSQVQLKQSGAEVKKPGASVKVSCKASGYTFTDEYMNWVRQAPGKSLEWMGYINPNNGGADYNQKFQGRVTMTVDQSISTAYMELSRLRSDDSAVYFCARLGYSNPYFDFWGQGTLVKVSS"
        }
    }

    print("=== Testing CGG annotation ===")
    processor = AnarciResultProcessor(test_input, numbering_scheme="cgg")
    result = processor.get_result_by_biologic_name("scfv")

    if not result or not result.chains:
        print("No result or chains found")
        return

    chain = result.chains[0]
    print(f"Chain: {chain.name}")
    print(f"Chain sequence length: {len(chain.sequence)}")

    for i, domain in enumerate(chain.domains):
        print(f"\nDomain {i}: {domain.domain_type}")
        print(f"Domain sequence length: {len(domain.sequence)}")

        if domain.alignment_details:
            print(f"Alignment details: {domain.alignment_details}")
            chain_type = domain.alignment_details.get("chain_type", "unknown")
            print(f"Chain type: {chain_type}")

        if domain.numbering:
            numbering = domain.numbering[0]
            print(f"Numbering length: {len(numbering)}")
            print(f"First 5 entries: {numbering[:5]}")
            print(f"Last 5 entries: {numbering[-5:]}")

            # Check position range
            positions = [
                entry[0][0]
                for entry in numbering
                if isinstance(entry, tuple) and len(entry) > 0
            ]
            print(f"Position range: {min(positions)} to {max(positions)}")

            # Test FR1 region detection
            pos_to_idx = RegionIndexHelper.build_pos_to_idx(numbering)
            print(
                f"Position to index mapping (first 10): {dict(list(pos_to_idx.items())[:10])}"
            )

            # Test finding FR1 region for K chain (positions 1-23 in CGG)
            fr1_start = (1, " ")
            fr1_stop = (23, " ")

            start_idx, stop_idx = RegionIndexHelper.find_region_indices(
                pos_to_idx, fr1_start, fr1_stop
            )
            print(f"FR1 indices: start_idx={start_idx}, stop_idx={stop_idx}")

            if start_idx is not None and stop_idx is not None:
                fr1_seq = RegionIndexHelper.extract_region_sequence(
                    numbering, start_idx, stop_idx
                )
                print(f"FR1 sequence: {fr1_seq}")
                print(f"FR1 sequence length: {len(fr1_seq)}")
            else:
                print("FR1 region not found!")

                # Check what positions are available
                available_positions = list(pos_to_idx.keys())
                print(
                    f"Available positions (first 10): {available_positions[:10]}"
                )

                # Check if position 1 exists
                if (1, " ") in pos_to_idx:
                    print("Position 1 exists in numbering")
                else:
                    print("Position 1 does NOT exist in numbering")

                # Check if position 23 exists
                if (23, " ") in pos_to_idx:
                    print("Position 23 exists in numbering")
                else:
                    print("Position 23 does NOT exist in numbering")

        # Check regions after annotation
        if hasattr(domain, "regions") and domain.regions:
            print(f"Regions found: {list(domain.regions.keys())}")
            for region_name, region in domain.regions.items():
                print(
                    f"  {region_name}: start={region.start}, stop={region.stop}, seq={region.sequence}"
                )
        else:
            print("No regions found")


if __name__ == "__main__":
    test_fr1_missing_debug()
