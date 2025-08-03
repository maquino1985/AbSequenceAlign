import logging
from typing import List, Dict, Any, Optional, Tuple
from app.models import SequenceInfo, NumberingScheme, ChainType

# Try to import ANARCI, fall back to our implementation if it fails
try:
    from anarci import anarci
except ImportError:
    from app.anarci_fallback import anarci

logger = logging.getLogger(__name__)


class AnnotationEngine:
    """Handles antibody sequence annotation using ANARCI"""
    
    def __init__(self):
        self.scheme_mapping = {
            NumberingScheme.IMGT: "imgt",
            NumberingScheme.KABAT: "kabat", 
            NumberingScheme.CHOTHIA: "chothia",
            NumberingScheme.MARTIN: "martin",
            NumberingScheme.AHO: "aho"
        }
    
    def annotate_sequences(self, sequences: List[str], 
                          numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
                          chain_type: Optional[ChainType] = None) -> List[SequenceInfo]:
        """
        Annotate antibody sequences using ANARCI
        
        Args:
            sequences: List of protein sequences
            numbering_scheme: Numbering scheme to use
            chain_type: Expected chain type (optional)
            
        Returns:
            List of SequenceInfo objects with annotations
        """
        if not sequences:
            return []
        
        # Convert numbering scheme to ANARCI format
        anarci_scheme = self.scheme_mapping[numbering_scheme]
        
        try:
            # Run ANARCI annotation
            results = anarci(sequences, scheme=anarci_scheme, allowed_species=['human', 'mouse', 'rat'])
            
            annotated_sequences = []
            
            for i, (sequence, result) in enumerate(zip(sequences, results)):
                seq_info = self._process_anarci_result(sequence, result, i)
                annotated_sequences.append(seq_info)
            
            return annotated_sequences
            
        except Exception as e:
            logger.error(f"ANARCI annotation failed: {e}")
            # Fallback: return basic sequence info without annotation
            return [SequenceInfo(sequence=seq, name=f"sequence_{i+1}") 
                   for i, seq in enumerate(sequences)]
    
    def _process_anarci_result(self, sequence: str, result: Tuple, index: int) -> SequenceInfo:
        """
        Process ANARCI result and extract relevant information
        
        Args:
            sequence: Original protein sequence
            result: ANARCI result tuple
            index: Sequence index
            
        Returns:
            SequenceInfo object with annotations
        """
        # ANARCI result structure: (numbering, alignment_details, hit_tables, chain_type, species)
        numbering, alignment_details, hit_tables, chain_type, species = result
        
        seq_info = SequenceInfo(
            sequence=sequence,
            name=f"sequence_{index+1}"
        )
        
        # Extract chain type
        if chain_type:
            seq_info.chain_type = chain_type
        
        # Extract species information
        if species:
            seq_info.species = species
        
        # Extract germline information from hit tables
        if hit_tables and len(hit_tables) > 0:
            # Get the best hit (highest score)
            best_hit = hit_tables[0]
            if best_hit and len(best_hit) > 0:
                germline_info = best_hit[0]  # First element contains germline info
                if isinstance(germline_info, dict) and 'germline' in germline_info:
                    seq_info.germline = germline_info['germline']
        
        # Extract isotype information (for heavy chains)
        if chain_type and chain_type.upper() in ['H', 'HEAVY']:
            seq_info.isotype = self._predict_isotype(sequence)
        
        return seq_info
    
    def _predict_isotype(self, sequence: str) -> Optional[str]:
        """
        Predict antibody isotype from sequence
        
        Args:
            sequence: Protein sequence
            
        Returns:
            Predicted isotype or None
        """
        # Simple isotype prediction based on C-terminal sequence patterns
        # This is a simplified version - in practice, you'd use more sophisticated methods
        
        isotype_patterns = {
            'IgG1': ['DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'],
            'IgG2': ['DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'],
            'IgG3': ['DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'],
            'IgG4': ['DKTHTCPPCPAPELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSRDELTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK'],
        }
        
        # Check for isotype-specific patterns in the C-terminal region
        c_terminal = sequence[-50:] if len(sequence) >= 50 else sequence
        
        for isotype, patterns in isotype_patterns.items():
            for pattern in patterns:
                if pattern in c_terminal:
                    return isotype
        
        return None
    
    def get_annotation_statistics(self, annotated_sequences: List[SequenceInfo]) -> Dict[str, Any]:
        """
        Calculate statistics from annotated sequences
        
        Args:
            annotated_sequences: List of annotated sequences
            
        Returns:
            Dictionary with annotation statistics
        """
        if not annotated_sequences:
            return {}
        
        # Count chain types
        chain_types = {}
        isotypes = {}
        species = {}
        
        for seq in annotated_sequences:
            if seq.chain_type:
                chain_types[seq.chain_type] = chain_types.get(seq.chain_type, 0) + 1
            
            if seq.isotype:
                isotypes[seq.isotype] = isotypes.get(seq.isotype, 0) + 1
            
            if seq.species:
                species[seq.species] = species.get(seq.species, 0) + 1
        
        return {
            "total_sequences": len(annotated_sequences),
            "chain_types": chain_types,
            "isotypes": isotypes,
            "species": species,
            "annotated_count": len([s for s in annotated_sequences if s.chain_type])
        } 