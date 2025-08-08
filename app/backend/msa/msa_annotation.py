from typing import List, Dict, Any, Optional
from ..models.models import MSAResult, MSASequence, MSAAnnotationResult, NumberingScheme
from ..annotation.annotation_engine import annotate_sequences_with_processor
from ..annotation.sequence_processor import SequenceProcessor


class MSAAnnotationEngine:
    """Engine for annotating sequences in MSA"""
    
    def __init__(self):
        self.sequence_processor = SequenceProcessor()
    
    def annotate_msa(self, msa_result: MSAResult, numbering_scheme: NumberingScheme) -> MSAAnnotationResult:
        """
        Annotate each sequence in the MSA individually
        
        Args:
            msa_result: MSA result with aligned sequences
            numbering_scheme: Numbering scheme to use for annotation
            
        Returns:
            MSAAnnotationResult with annotated sequences and region mappings
        """
        # Extract original sequences for annotation
        sequences_for_annotation = []
        for msa_seq in msa_result.sequences:
            # Create SequenceInput for annotation
            from ..models.models import SequenceInput
            seq_input = SequenceInput(
                name=msa_seq.name,
                heavy_chain=msa_seq.original_sequence  # Assume heavy chain for now
            )
            sequences_for_annotation.append(seq_input)
        
        # Annotate sequences using existing annotation engine
        annotation_result = annotate_sequences_with_processor(
            sequences=sequences_for_annotation,
            numbering_scheme=numbering_scheme
        )
        
        # Map annotations back to MSA sequences
        annotated_sequences = []
        region_mappings = {}
        
        for i, msa_seq in enumerate(msa_result.sequences):
            if i < len(annotation_result.sequences):
                # Get annotations for this sequence
                seq_info = annotation_result.sequences[i]
                annotations = self._extract_annotations(seq_info)
                
                # Create annotated MSA sequence
                annotated_seq = MSASequence(
                    name=msa_seq.name,
                    original_sequence=msa_seq.original_sequence,
                    aligned_sequence=msa_seq.aligned_sequence,
                    start_position=msa_seq.start_position,
                    end_position=msa_seq.end_position,
                    gaps=msa_seq.gaps,
                    annotations=annotations
                )
                annotated_sequences.append(annotated_seq)
                
                # Add to region mappings
                for annotation in annotations:
                    region_name = annotation.get('name', 'unknown')
                    if region_name not in region_mappings:
                        region_mappings[region_name] = []
                    region_mappings[region_name].append({
                        'sequence_name': msa_seq.name,
                        'start': annotation.get('start'),
                        'stop': annotation.get('stop'),
                        'sequence': annotation.get('sequence', ''),
                        'color': annotation.get('color', '#000000')
                    })
        
        # Create annotation result
        annotation_result = MSAAnnotationResult(
            msa_id=msa_result.msa_id,
            annotated_sequences=annotated_sequences,
            numbering_scheme=numbering_scheme,
            region_mappings=region_mappings
        )
        
        return annotation_result
    
    def _extract_annotations(self, seq_info) -> List[Dict[str, Any]]:
        """Extract annotations from sequence info"""
        annotations = []
        
        if hasattr(seq_info, 'regions') and seq_info.regions:
            for region_name, region_data in seq_info.regions.items():
                annotation = {
                    'name': region_name,
                    'start': region_data.start,
                    'stop': region_data.stop,
                    'sequence': region_data.sequence,
                    'color': self._get_region_color(region_name)
                }
                annotations.append(annotation)
        
        return annotations
    
    def _get_region_color(self, region_name: str) -> str:
        """Get color for region based on name"""
        color_map = {
            'FR1': '#FF6B6B',
            'CDR1': '#4ECDC4',
            'FR2': '#45B7D1',
            'CDR2': '#96CEB4',
            'FR3': '#FFEAA7',
            'CDR3': '#DDA0DD',
            'FR4': '#98D8C8',
            'VH': '#FF6B6B',
            'VL': '#4ECDC4',
            'CH1': '#45B7D1',
            'CH2': '#96CEB4',
            'CH3': '#FFEAA7',
            'CL': '#DDA0DD'
        }
        
        return color_map.get(region_name, '#CCCCCC')
    
    def get_region_positions_in_alignment(self, msa_result: MSAResult, 
                                        region_name: str) -> List[Dict[str, Any]]:
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
                    if annotation.get('name') == region_name:
                        # Map original positions to aligned positions
                        aligned_start, aligned_stop = self._map_positions_to_alignment(
                            msa_seq.original_sequence,
                            msa_seq.aligned_sequence,
                            annotation.get('start', 0),
                            annotation.get('stop', 0)
                        )
                        
                        region_positions.append({
                            'sequence_name': msa_seq.name,
                            'original_start': annotation.get('start'),
                            'original_stop': annotation.get('stop'),
                            'aligned_start': aligned_start,
                            'aligned_stop': aligned_stop,
                            'color': annotation.get('color', '#000000')
                        })
                        break
        
        return region_positions
    
    def _map_positions_to_alignment(self, original_seq: str, aligned_seq: str, 
                                   start: int, stop: int) -> tuple[int, int]:
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
        ungapped_aligned = aligned_seq.replace('-', '')
        
        if ungapped_aligned != original_seq:
            # Handle case where sequences don't match
            return start, stop
        
        # Map positions
        aligned_start = 0
        aligned_stop = 0
        orig_pos = 0
        
        for i, char in enumerate(aligned_seq):
            if char != '-':
                if orig_pos == start:
                    aligned_start = i
                if orig_pos == stop:
                    aligned_stop = i
                    break
                orig_pos += 1
        
        return aligned_start, aligned_stop
