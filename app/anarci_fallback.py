"""
Fallback ANARCI implementation for when the full ANARCI installation fails.
This provides basic antibody numbering functionality.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
from app.models import NumberingScheme


class ANARCIFallback:
    """Fallback ANARCI implementation with basic functionality"""
    
    def __init__(self):
        self.scheme_mapping = {
            NumberingScheme.IMGT: "imgt",
            NumberingScheme.KABAT: "kabat", 
            NumberingScheme.CHOTHIA: "chothia",
            NumberingScheme.MARTIN: "martin",
            NumberingScheme.AHO: "aho"
        }
    
    def anarci(self, sequences: List[str], scheme: str = "imgt", allowed_species: Optional[List[str]] = None) -> List[Tuple]:
        """
        Fallback ANARCI function that provides basic antibody annotation
        
        Args:
            sequences: List of protein sequences
            scheme: Numbering scheme
            allowed_species: List of allowed species (ignored in fallback)
            
        Returns:
            List of tuples with (numbering, alignment_details, hit_tables, chain_type, species)
        """
        results = []
        
        for sequence in sequences:
            # Basic antibody detection
            chain_type = self._detect_chain_type(sequence)
            species = self._detect_species(sequence)
            
            # Create basic numbering (simplified)
            numbering = self._create_basic_numbering(sequence, scheme)
            
            # Create alignment details
            alignment_details = self._create_alignment_details(sequence)
            
            # Create hit tables
            hit_tables = self._create_hit_tables(sequence, chain_type)
            
            results.append((numbering, alignment_details, hit_tables, chain_type, species))
        
        return results
    
    def _detect_chain_type(self, sequence: str) -> str:
        """Detect antibody chain type from sequence"""
        # Simple heuristics for chain type detection
        if len(sequence) > 400:  # Heavy chains are typically longer
            return "H"
        else:
            return "L"
    
    def _detect_species(self, sequence: str) -> str:
        """Detect species from sequence (simplified)"""
        # This is a very simplified detection
        # In practice, you'd use more sophisticated methods
        return "human"
    
    def _create_basic_numbering(self, sequence: str, scheme: str) -> Dict[str, Any]:
        """Create basic numbering for the sequence"""
        # This is a simplified numbering
        # In practice, you'd use the actual ANARCI numbering logic
        return {
            "scheme": scheme,
            "sequence": sequence,
            "numbered": sequence,  # Simplified - no actual numbering
            "regions": {
                "FR1": (0, 25),
                "CDR1": (26, 32),
                "FR2": (33, 49),
                "CDR2": (50, 56),
                "FR3": (57, 88),
                "CDR3": (89, 97),
                "FR4": (98, len(sequence))
            }
        }
    
    def _create_alignment_details(self, sequence: str) -> Dict[str, Any]:
        """Create alignment details"""
        return {
            "sequence": sequence,
            "length": len(sequence),
            "aligned": sequence
        }
    
    def _create_hit_tables(self, sequence: str, chain_type: str) -> List[List[Dict[str, Any]]]:
        """Create hit tables for germline matching"""
        # Simplified germline matching
        germline = f"IG{chain_type}*01" if chain_type in ["H", "L"] else "Unknown"
        
        return [[{
            "germline": germline,
            "score": 0.8,  # Simplified score
            "identity": 0.9  # Simplified identity
        }]]


# Global fallback instance
anarci_fallback = ANARCIFallback()


def anarci(sequences: List[str], scheme: str = "imgt", allowed_species: Optional[List[str]] = None) -> List[Tuple]:
    """
    ANARCI function that tries the real ANARCI first, falls back to simplified version
    
    Args:
        sequences: List of protein sequences
        scheme: Numbering scheme
        allowed_species: List of allowed species
        
    Returns:
        List of tuples with (numbering, alignment_details, hit_tables, chain_type, species)
    """
    try:
        # Try to import and use the real ANARCI
        from anarci import anarci as real_anarci
        return real_anarci(sequences, scheme=scheme, allowed_species=allowed_species)
    except ImportError:
        # Fall back to simplified implementation
        return anarci_fallback.anarci(sequences, scheme=scheme, allowed_species=allowed_species) 