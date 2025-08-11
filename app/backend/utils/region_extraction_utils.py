"""
Region extraction utilities for antibody sequence analysis.
Uses the existing numbering schemes to properly extract CDR and FR regions.
"""

from typing import Dict, List, Tuple, Optional, Any
from backend.core.interfaces import RegionExtractionInterface
from backend.numbering.imgt import IMGT_REGIONS
from backend.numbering.kabat import KABAT_REGIONS
from backend.numbering.chothia import CHOTHIA_REGIONS
from backend.logger import logger


class RegionExtractionUtils(RegionExtractionInterface):
    """Utilities for extracting regions using proper numbering schemes"""

    # Mapping of numbering scheme names to their region definitions
    NUMBERING_SCHEMES = {
        "IMGT": IMGT_REGIONS,
        "KABAT": KABAT_REGIONS,
        "CHOTHIA": CHOTHIA_REGIONS,
    }

    def get_region_boundaries(
        self, chain_type: str, region_type: str
    ) -> Optional[Tuple[int, int]]:
        """
        Get region boundaries for a specific chain type and region.

        Args:
            chain_type: The chain type (H for heavy, L for light)
            region_type: The region type (CDR1, CDR2, CDR3, FR1, FR2, FR3, FR4)

        Returns:
            Tuple of (start_position, end_position) or None if not found
        """
        try:
            scheme = self.NUMBERING_SCHEMES.get(self.numbering_scheme)
            if not scheme:
                logger.warning(
                    f"Unknown numbering scheme: {self.numbering_scheme}"
                )
                return None

            chain_regions = scheme.get(chain_type.upper())
            if not chain_regions:
                logger.warning(
                    f"Unknown chain type {chain_type} for scheme {self.numbering_scheme}"
                )
                return None

            region_boundaries = chain_regions.get(region_type.upper())
            if not region_boundaries:
                logger.warning(
                    f"Unknown region type {region_type} for chain {chain_type}"
                )
                return None

            # Extract start and end positions from the boundary definition
            start_pos = region_boundaries[0][0]  # First tuple, first element
            end_pos = region_boundaries[1][0]  # Second tuple, first element

            return (start_pos, end_pos)

        except Exception as e:
            logger.error(f"Error getting region boundaries: {e}")
            return None

    def get_all_regions(self, chain_type: str) -> Dict[str, Tuple[int, int]]:
        """
        Get all region boundaries for a specific chain type.

        Args:
            chain_type: The chain type (H for heavy, L for light)

        Returns:
            Dictionary mapping region names to (start, end) positions
        """
        regions = {}

        try:
            scheme = self.NUMBERING_SCHEMES.get(self.numbering_scheme)
            if not scheme:
                logger.warning(
                    f"Unknown numbering scheme: {self.numbering_scheme}"
                )
                return regions

            chain_regions = scheme.get(chain_type.upper())
            if not chain_regions:
                logger.warning(
                    f"Unknown chain type {chain_type} for scheme {self.numbering_scheme}"
                )
                return regions

            for region_name, boundaries in chain_regions.items():
                start_pos = boundaries[0][0]
                end_pos = boundaries[1][0]
                regions[region_name] = (start_pos, end_pos)

        except Exception as e:
            logger.error(f"Error getting all region boundaries: {e}")

        return regions

    def get_cdr_regions(self, chain_type: str) -> Dict[str, Tuple[int, int]]:
        """
        Get CDR region boundaries for a specific chain type.

        Args:
            chain_type: The chain type (H for heavy, L for light)

        Returns:
            Dictionary mapping CDR names to (start, end) positions
        """
        all_regions = self.get_all_regions(chain_type)
        return {k: v for k, v in all_regions.items() if k.startswith("CDR")}

    def get_framework_regions(
        self, chain_type: str
    ) -> Dict[str, Tuple[int, int]]:
        """
        Get framework region boundaries for a specific chain type.

        Args:
            chain_type: The chain type (H for heavy, L for light)

        Returns:
            Dictionary mapping FR names to (start, end) positions
        """
        all_regions = self.get_all_regions(chain_type)
        return {k: v for k, v in all_regions.items() if k.startswith("FR")}

    def find_position_in_sequence(
        self, numbered: List[Any], position: int
    ) -> Optional[int]:
        """
        Find the actual index in the numbered sequence for a given position number.

        Args:
            numbered: The numbered sequence from ANARCI
            position: The position number to find

        Returns:
            Index in the numbered sequence or None if not found
        """
        try:
            # First try to find exact position match
            for i, aa_data in enumerate(numbered):
                if isinstance(aa_data, dict) and "position" in aa_data:
                    if aa_data["position"] == position:
                        return i
                elif (
                    hasattr(aa_data, "position")
                    and aa_data.position == position
                ):
                    return i

            # If exact position not found, try to find closest position
            for i, aa_data in enumerate(numbered):
                if isinstance(aa_data, dict) and "position" in aa_data:
                    if aa_data["position"] >= position:
                        return i
                elif (
                    hasattr(aa_data, "position")
                    and aa_data.position >= position
                ):
                    return i

            return None

        except Exception as e:
            logger.error(
                f"Error finding position {position} in numbered sequence: {e}"
            )
            return None

    def extract_region_sequence(
        self, numbered: List[Any], start_position: int, end_position: int
    ) -> Optional[str]:
        """
        Extract a region sequence from the numbered sequence.

        Args:
            numbered: The numbered sequence from ANARCI
            start_position: Start position in numbering scheme
            end_position: End position in numbering scheme

        Returns:
            The extracted sequence or None if extraction failed
        """
        try:
            start_idx = self.find_position_in_sequence(
                numbered, start_position
            )
            end_idx = self.find_position_in_sequence(numbered, end_position)

            if start_idx is None or end_idx is None:
                logger.warning(
                    f"Could not find positions {start_position}-{end_position} in numbered sequence"
                )
                return None

            # Ensure start_idx <= end_idx
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx

            # Extract the sequence
            region_data = numbered[start_idx : end_idx + 1]
            sequence = ""

            for aa_data in region_data:
                if isinstance(aa_data, dict):
                    sequence += aa_data.get("amino_acid", "")
                elif hasattr(aa_data, "amino_acid"):
                    sequence += aa_data.amino_acid
                else:
                    sequence += str(aa_data)

            return sequence

        except Exception as e:
            logger.error(
                f"Error extracting region {start_position}-{end_position}: {e}"
            )
            return None

    def detect_chain_type(self, sequence: str) -> str:
        """
        Detect chain type from sequence characteristics.

        Args:
            sequence: The amino acid sequence

        Returns:
            Chain type ("H" for heavy, "L" for light)
        """
        try:
            # Simple heuristics for chain type detection
            # Heavy chains typically have longer CDR3 regions
            # This is a simplified approach - in practice, you'd use more sophisticated methods

            if len(sequence) > 400:  # Heavy chains are typically longer
                return "H"
            else:
                return "L"

        except Exception as e:
            logger.error(f"Error detecting chain type: {e}")
            return "H"  # Default to heavy chain
