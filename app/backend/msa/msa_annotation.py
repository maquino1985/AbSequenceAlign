from typing import List, Dict, Any

from backend.annotation.annotation_engine import (
    annotate_sequences_with_processor,
)
from backend.annotation.sequence_processor import SequenceProcessor
from backend.logger import logger
from backend.models.models import (
    MSAResult,
    MSASequence,
    MSAAnnotationResult,
    NumberingScheme,
    SequenceInput,
)


class MSAAnnotationEngine:
    """Enhanced MSA Annotation Engine with individual sequence annotation"""

    def __init__(self):
        self.sequence_processor = SequenceProcessor()

    def annotate_msa(
        self,
        msa_result: MSAResult,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> MSAAnnotationResult:
        """
        Annotate MSA with region information for each sequence

        Args:
            msa_result: MSA result containing aligned sequences
            numbering_scheme: Numbering scheme for annotation

        Returns:
            MSAAnnotationResult with enhanced annotations
        """
        try:
            # Create SequenceInput objects for annotation
            sequence_inputs = []
            for seq in msa_result.sequences:
                seq_input = SequenceInput(
                    name=seq.name,
                    heavy_chain=seq.original_sequence,  # Assume heavy chain for now
                )
                sequence_inputs.append(seq_input)

            # Annotate sequences using existing annotation engine
            annotation_result = annotate_sequences_with_processor(
                sequences=sequence_inputs, numbering_scheme=numbering_scheme
            )

            # Map annotations back to MSA sequences
            annotated_sequences = []
            all_regions = []

            for i, msa_seq in enumerate(msa_result.sequences):
                sequence_regions = []

                if i < len(annotation_result.sequences):
                    # Get annotations for this sequence
                    seq_info = annotation_result.sequences[i]

                    # Extract regions if they exist
                    if hasattr(seq_info, "regions") and seq_info.regions:
                        for (
                            region_name,
                            region_data,
                        ) in seq_info.regions.items():
                            # Map region positions to aligned sequence positions
                            aligned_start, aligned_stop = (
                                self._map_region_to_aligned(
                                    region_data,
                                    msa_seq.original_sequence,
                                    msa_seq.aligned_sequence,
                                )
                            )

                            region_info = {
                                "id": f"{msa_seq.name}_{region_name}",
                                "name": region_name,
                                "start": aligned_start,
                                "stop": aligned_stop,
                                "sequence": (
                                    region_data.sequence
                                    if hasattr(region_data, "sequence")
                                    else ""
                                ),
                                "type": (
                                    "CDR" if "CDR" in region_name else "FR"
                                ),
                                "color": self._get_region_color(region_name),
                                "original_start": (
                                    region_data.start
                                    if hasattr(region_data, "start")
                                    else 0
                                ),
                                "original_stop": (
                                    region_data.stop
                                    if hasattr(region_data, "stop")
                                    else 0
                                ),
                            }
                            sequence_regions.append(region_info)
                            all_regions.append(region_info)

                # Create enhanced sequence with annotations
                enhanced_seq = MSASequence(
                    name=msa_seq.name,
                    original_sequence=msa_seq.original_sequence,
                    aligned_sequence=msa_seq.aligned_sequence,
                    start_position=msa_seq.start_position,
                    end_position=msa_seq.end_position,
                    gaps=msa_seq.gaps,
                    annotations=sequence_regions,
                )
                annotated_sequences.append(enhanced_seq)

            # Create region mappings
            region_mappings = {}
            for region in all_regions:
                region_name = region["name"]
                if region_name not in region_mappings:
                    region_mappings[region_name] = []
                region_mappings[region_name].append(
                    {
                        "sequence_name": region["id"].split("_")[0],
                        "start": region["start"],
                        "stop": region["stop"],
                        "sequence": region["sequence"],
                        "color": region["color"],
                    }
                )

            return MSAAnnotationResult(
                msa_id=msa_result.msa_id,
                annotated_sequences=annotated_sequences,
                numbering_scheme=numbering_scheme,
                region_mappings=region_mappings,
            )

        except Exception as e:
            logger.error(f"MSA annotation failed: {e}")
            raise RuntimeError(f"MSA annotation failed: {e}")

    def _map_region_to_aligned(
        self, region_data: Any, original_seq: str, aligned_seq: str
    ) -> tuple[int, int]:
        """
        Map region positions from original sequence to aligned sequence positions

        Args:
            region_data: Region information from annotation
            original_seq: Original unaligned sequence
            aligned_seq: Aligned sequence with gaps

        Returns:
            Tuple of (aligned_start, aligned_stop) positions
        """
        # Find the region sequence in the original sequence
        region_seq = getattr(region_data, "sequence", "")
        orig_start = original_seq.find(region_seq) if region_seq else -1

        if orig_start == -1:
            # Fallback: use the region start/stop from annotation
            start_val = getattr(region_data, "start", 0)
            stop_val = getattr(region_data, "stop", 0)

            if isinstance(start_val, (list, tuple)):
                orig_start = start_val[0] - 1  # Convert to 0-based
            else:
                orig_start = start_val - 1 if start_val > 0 else 0

            if isinstance(stop_val, (list, tuple)):
                orig_stop = stop_val[0] - 1
            else:
                orig_stop = stop_val - 1 if stop_val > 0 else 0
        else:
            orig_stop = orig_start + len(region_seq) - 1

        # Map to aligned sequence positions
        aligned_start = self._map_position_to_aligned(
            orig_start, original_seq, aligned_seq
        )
        aligned_stop = self._map_position_to_aligned(
            orig_stop, original_seq, aligned_seq
        )

        return aligned_start, aligned_stop

    def _map_position_to_aligned(
        self, orig_pos: int, original_seq: str, aligned_seq: str
    ) -> int:
        """
        Map a position from original sequence to aligned sequence

        Args:
            orig_pos: Position in original sequence (0-based)
            original_seq: Original sequence
            aligned_seq: Aligned sequence with gaps

        Returns:
            Position in aligned sequence (0-based)
        """
        if orig_pos >= len(original_seq):
            return len(aligned_seq) - 1

        # Count gaps up to the target position
        gap_count = 0
        orig_count = 0

        for i, char in enumerate(aligned_seq):
            if char == "-":
                gap_count += 1
            else:
                if orig_count == orig_pos:
                    return i
                orig_count += 1

        return len(aligned_seq) - 1

    def _get_region_color(self, region_name: str) -> str:
        """Get color for region based on name"""
        color_map = {
            "FR1": "#FF6B6B",  # Red
            "CDR1": "#4ECDC4",  # Teal
            "FR2": "#45B7D1",  # Light Blue
            "CDR2": "#96CEB4",  # Green
            "FR3": "#FFEAA7",  # Yellow
            "CDR3": "#DDA0DD",  # Purple
            "FR4": "#98D8C8",  # Mint
            "VH": "#FF6B6B",  # Red
            "VL": "#4ECDC4",  # Teal
            "CH1": "#45B7D1",  # Light Blue
            "CH2": "#96CEB4",  # Green
            "CH3": "#FFEAA7",  # Yellow
            "CL": "#DDA0DD",  # Purple
        }

        return color_map.get(region_name, "#CCCCCC")

    def get_region_positions_in_alignment(
        self, msa_result: MSAResult, region_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get positions of a specific region across all sequences in the alignment

        Args:
            msa_result: MSA result
            region_name: Name of the region to find

        Returns:
            List of region positions for each sequence
        """
        region_positions = []

        for msa_seq in msa_result.sequences:
            if msa_seq.annotations:
                for annotation in msa_seq.annotations:
                    if annotation.get("name") == region_name:
                        # Map original positions to aligned positions
                        aligned_start, aligned_stop = (
                            self._map_positions_to_alignment(
                                msa_seq.original_sequence,
                                msa_seq.aligned_sequence,
                                annotation.get("start", 0),
                                annotation.get("stop", 0),
                            )
                        )

                        region_positions.append(
                            {
                                "sequence_name": msa_seq.name,
                                "original_start": annotation.get("start"),
                                "original_stop": annotation.get("stop"),
                                "aligned_start": aligned_start,
                                "aligned_stop": aligned_stop,
                                "color": annotation.get("color", "#000000"),
                            }
                        )
                        break

        return region_positions

    def _map_positions_to_alignment(
        self, original_seq: str, aligned_seq: str, start: int, stop: int
    ) -> tuple[int, int]:
        """
        Map positions from original sequence to aligned sequence

        Args:
            original_seq: Original sequence
            aligned_seq: Aligned sequence with gaps
            start: Start position in original sequence
            stop: Stop position in original sequence

        Returns:
            Tuple of (aligned_start, aligned_stop)
        """
        if not original_seq or not aligned_seq:
            return start, stop

        # Remove gaps from aligned sequence to get original
        ungapped_aligned = aligned_seq.replace("-", "")

        if ungapped_aligned != original_seq:
            # Handle case where sequences don't match
            return start, stop

        # Map positions
        aligned_start = 0
        aligned_stop = 0
        orig_pos = 0

        for i, char in enumerate(aligned_seq):
            if char != "-":
                if orig_pos == start:
                    aligned_start = i
                if orig_pos == stop:
                    aligned_stop = i
                    break
                orig_pos += 1

        return aligned_start, aligned_stop

    def _extract_annotations(self, seq_info: Any) -> List[Dict[str, Any]]:
        """
        Extract annotations from sequence info

        Args:
            seq_info: Sequence info object with regions

        Returns:
            List of region annotations
        """
        annotations = []

        if not hasattr(seq_info, "regions") or not seq_info.regions:
            return annotations

        for region_name, region_data in seq_info.regions.items():
            annotation = {
                "name": region_name,
                "start": (
                    region_data.get("start", 0)
                    if isinstance(region_data, dict)
                    else getattr(region_data, "start", 0)
                ),
                "stop": (
                    region_data.get("stop", 0)
                    if isinstance(region_data, dict)
                    else getattr(region_data, "stop", 0)
                ),
                "sequence": (
                    region_data.get("sequence", "")
                    if isinstance(region_data, dict)
                    else getattr(region_data, "sequence", "")
                ),
                "color": self._get_region_color(region_name),
            }
            annotations.append(annotation)

        return annotations
