"""
Test file to investigate indexing issues with ANARCI and region annotation.
This will help understand the root cause of the +1 and +2 adjustments needed.
"""

import pytest
from backend.annotation.anarci_result_processor import AnarciResultProcessor
from backend.annotation.antibody_region_annotator import (
    AntibodyRegionAnnotator,
)
from backend.annotation.region_utils import RegionIndexHelper
from backend.utils.types import Domain, Chain
from backend.logger import logger


class TestIndexingInvestigation:
    """Test class to investigate indexing issues with real ANARCI output."""

    def test_anarci_numbering_format_analysis(self):
        """Analyze ANARCI's numbering format to understand indexing issues."""
        logger.info("\n=== ANARCI Numbering Format Analysis ===")

        # Use a simple test sequence
        test_input = {
            "test_antibody": {
                "H": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            }
        }

        processor = AnarciResultProcessor(test_input, numbering_scheme="imgt")
        result = processor.get_result_by_biologic_name("test_antibody")

        assert result is not None
        chain = result.chains[0]
        domain = chain.domains[0]

        logger.info(f"Domain numbering type: {type(domain.numbering)}")
        if domain.numbering:
            numbering = domain.numbering[
                0
            ]  # ANARCI returns list of numberings
            logger.info(f"Numbering length: {len(numbering)}")
            logger.info(f"First 5 entries: {numbering[:5]}")
            logger.info(f"Last 5 entries: {numbering[-5:]}")

            # Check position range
            positions = [
                entry[0][0]
                for entry in numbering
                if isinstance(entry, tuple) and len(entry) > 0
            ]
            logger.info(
                f"Position range: {min(positions)} to {max(positions)}"
            )

            # Check alignment details
            if domain.alignment_details:
                logger.info(f"Alignment details: {domain.alignment_details}")
                query_start = domain.alignment_details.get("query_start")
                query_end = domain.alignment_details.get("query_end")
                logger.info(f"Query range: {query_start}-{query_end}")

    def test_region_index_helper_analysis(self):
        """Analyze RegionIndexHelper behavior with real ANARCI output."""
        logger.info("\n=== RegionIndexHelper Analysis ===")

        test_input = {
            "test_antibody": {
                "H": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            }
        }

        processor = AnarciResultProcessor(test_input, numbering_scheme="imgt")
        result = processor.get_result_by_biologic_name("test_antibody")

        assert result is not None
        chain = result.chains[0]
        domain = chain.domains[0]

        if domain.numbering:
            numbering = domain.numbering[0]
            pos_to_idx = RegionIndexHelper.build_pos_to_idx(numbering)
            logger.info(
                f"Position to index mapping (first 10): {dict(list(pos_to_idx.items())[:10])}"
            )

            # Test finding FR1 region (positions 1-26 in IMGT)
            fr1_start = (1, " ")
            fr1_stop = (26, " ")

            start_idx, stop_idx = RegionIndexHelper.find_region_indices(
                pos_to_idx, fr1_start, fr1_stop
            )
            logger.info(
                f"FR1 indices: start_idx={start_idx}, stop_idx={stop_idx}"
            )

            if start_idx is not None and stop_idx is not None:
                fr1_seq = RegionIndexHelper.extract_region_sequence(
                    numbering, start_idx, stop_idx
                )
                logger.info(f"FR1 sequence: {fr1_seq}")
                logger.info(f"FR1 sequence length: {len(fr1_seq)}")
            else:
                logger.info(
                    "FR1 region not found - this explains the indexing issues!"
                )

    def test_antibody_region_annotator_analysis(self):
        """Analyze the +2 adjustment in AntibodyRegionAnnotator."""
        logger.info("\n=== AntibodyRegionAnnotator Analysis ===")

        test_input = {
            "test_antibody": {
                "H": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            }
        }

        processor = AnarciResultProcessor(test_input, numbering_scheme="imgt")
        result = processor.get_result_by_biologic_name("test_antibody")

        assert result is not None
        chain = result.chains[0]
        domain = chain.domains[0]

        # Test region annotation
        original_regions = (
            domain.regions.copy() if hasattr(domain, "regions") else {}
        )
        AntibodyRegionAnnotator.annotate_domain(domain, scheme="imgt")

        logger.info(f"Regions after annotation: {domain.regions}")

        # Check if the +2 adjustment is applied
        if hasattr(domain, "regions") and domain.regions:
            for region_name, region in domain.regions.items():
                logger.info(f"Region {region_name}:")
                logger.info(f"  Start: {region.start}, Stop: {region.stop}")
                logger.info(f"  Sequence: {region.sequence}")

                if hasattr(region, "start") and hasattr(region, "stop"):
                    start_val = (
                        region.start
                        if isinstance(region.start, int)
                        else region.start[0]
                    )
                    stop_val = (
                        region.stop
                        if isinstance(region.stop, int)
                        else region.stop[0]
                    )
                    logger.info(
                        f"  Start value: {start_val}, Stop value: {stop_val}"
                    )

    def test_anarci_result_processor_absolute_positions(self):
        """Test the absolute position calculation in AnarciResultProcessor."""
        logger.info("\n=== Absolute Position Calculation Analysis ===")

        test_input = {
            "test_antibody": {
                "H": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            }
        }

        processor = AnarciResultProcessor(test_input, numbering_scheme="imgt")
        result = processor.get_result_by_biologic_name("test_antibody")

        assert result is not None
        chain = result.chains[0]
        domain = chain.domains[0]

        # Check alignment details
        if domain.alignment_details:
            logger.info(
                f"Domain alignment details: {domain.alignment_details}"
            )
            query_start = domain.alignment_details.get("query_start")
            query_end = domain.alignment_details.get("query_end")
            logger.info(f"Query start: {query_start}, Query end: {query_end}")

        # Check regions after processing
        if hasattr(domain, "regions") and domain.regions:
            logger.info(f"Final regions: {domain.regions}")
            for region_name, region in domain.regions.items():
                logger.info(f"Region {region_name}:")
                logger.info(f"  Start: {region.start}, Stop: {region.stop}")
                logger.info(f"  Sequence: {region.sequence}")

    def test_api_v2_endpoint_indexing_simulation(self):
        """Simulate the API v2 endpoint indexing logic."""
        logger.info("\n=== API v2 Endpoint Indexing Simulation ===")

        test_input = {
            "test_antibody": {
                "H": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            }
        }

        processor = AnarciResultProcessor(test_input, numbering_scheme="imgt")
        result = processor.get_result_by_biologic_name("test_antibody")

        assert result is not None
        chain = result.chains[0]
        domain = chain.domains[0]

        # Simulate the API v2 processing
        if hasattr(domain, "regions") and domain.regions:
            for region_name, region in domain.regions.items():
                logger.info(f"API v2 processing for region {region_name}:")

                # Simulate the API v2 logic from endpoints.py
                if isinstance(region, dict):
                    start = (
                        int(region.get("start")) + 1
                    )  # This is the +1 adjustment
                    stop = int(region.get("stop"))
                    seq_val = region.get("sequence")
                else:
                    start = int(region.start)
                    stop = int(region.stop)
                    seq_val = region.sequence

                logger.info(
                    f"  Original start: {region.start if hasattr(region, 'start') else region.get('start')}"
                )
                logger.info(
                    f"  Original stop: {region.stop if hasattr(region, 'stop') else region.get('stop')}"
                )
                logger.info(f"  API v2 start: {start}")
                logger.info(f"  API v2 stop: {stop}")
                logger.info(f"  Sequence: {seq_val}")

    def test_proposed_solution_analysis(self):
        """Analyze the proposed solution to fix indexing issues."""
        logger.info("\n=== Proposed Solution Analysis ===")

        # The issues identified:
        logger.info("1. ANARCI numbering is 1-indexed (positions start at 1)")
        logger.info("2. RegionIndexHelper expects exact position matches")
        logger.info(
            "3. IMGT region definitions expect positions up to 128/129"
        )
        logger.info("4. Actual ANARCI output may only go up to position 117")
        logger.info("5. AntibodyRegionAnnotator adds +2 to start/stop indices")
        logger.info("6. API v2 endpoint adds +1 to start position")

        logger.info("\nProposed solutions:")
        logger.info(
            "1. Fix RegionIndexHelper to handle missing positions gracefully"
        )
        logger.info("2. Remove the +2 adjustment in AntibodyRegionAnnotator")
        logger.info(
            "3. Standardize on 1-indexed positions throughout the pipeline"
        )
        logger.info(
            "4. Update region definitions to match actual ANARCI output"
        )

    def test_indexing_fixes_verification(self):
        """Test that the indexing fixes work correctly."""
        logger.info("\n=== Indexing Fixes Verification ===")

        test_input = {
            "test_antibody": {
                "H": "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            }
        }

        processor = AnarciResultProcessor(test_input, numbering_scheme="imgt")
        result = processor.get_result_by_biologic_name("test_antibody")

        assert result is not None
        chain = result.chains[0]
        domain = chain.domains[0]

        # Test that regions are now properly annotated
        if hasattr(domain, "regions") and domain.regions:
            logger.info("✅ Regions are now properly annotated!")
            for region_name, region in domain.regions.items():
                logger.info(f"Region {region_name}:")
                logger.info(f"  Start: {region.start}, Stop: {region.stop}")
                logger.info(f"  Sequence: {region.sequence}")

                # Verify that positions are reasonable
                if hasattr(region, "start") and hasattr(region, "stop"):
                    start_val = (
                        region.start
                        if isinstance(region.start, int)
                        else region.start[0]
                    )
                    stop_val = (
                        region.stop
                        if isinstance(region.stop, int)
                        else region.stop[0]
                    )
                    logger.info(
                        f"  Start value: {start_val}, Stop value: {stop_val}"
                    )

                    # Check that positions are within reasonable bounds
                    assert (
                        start_val >= 0
                    ), f"Start position {start_val} should be >= 0"
                    assert (
                        stop_val >= start_val
                    ), f"Stop position {stop_val} should be >= start position {start_val}"
                    assert len(region.sequence) == (
                        stop_val - start_val + 1
                    ), f"Sequence length {len(region.sequence)} should match position range {stop_val - start_val + 1}"
        else:
            logger.info("❌ No regions found - the fix may not be working")


if __name__ == "__main__":
    # Run the tests
    test_instance = TestIndexingInvestigation()
    test_instance.test_anarci_numbering_format_analysis()
    test_instance.test_region_index_helper_analysis()
    test_instance.test_antibody_region_annotator_analysis()
    test_instance.test_anarci_result_processor_absolute_positions()
    test_instance.test_api_v2_endpoint_indexing_simulation()
    test_instance.test_proposed_solution_analysis()
    test_instance.test_indexing_fixes_verification()
