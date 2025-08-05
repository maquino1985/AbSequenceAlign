import logging
import pathlib
from typing import List, Dict, Any, Optional, Tuple
from app.models import SequenceInfo, NumberingScheme, ChainType
from app.config import HMM_MODEL_DIR, HMM_MODEL_FILE
import os

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
        
        # Ensure input is a list of (name, sequence) tuples for ANARCI
        anarci_input = [(f"sequence_{i+1}", seq) for i, seq in enumerate(sequences)]
        try:
            # Run ANARCI annotation
            results = anarci(anarci_input, scheme=anarci_scheme, allowed_species=['human', 'mouse', 'rat'])
            
            annotated_sequences = []
            for seq_idx, result in enumerate(results):
                numbering, alignment_details, hit_tables = result if (isinstance(result, tuple) and len(result) == 3) else (None, None, None)
                if not alignment_details or not isinstance(alignment_details, list):
                    # fallback: treat as single domain, old behavior
                    seq_info = self._process_anarci_result(sequences[seq_idx], result, 0)
                    annotated_sequences.append(seq_info)
                    continue
                # For each domain/component in the sequence
                for dom_idx, domain_detail in enumerate(alignment_details):
                    # Get corresponding numbering and hit_table if available
                    domain_numbering = numbering[dom_idx] if numbering and len(numbering) > dom_idx else None
                    domain_hit_table = hit_tables[dom_idx] if hit_tables and len(hit_tables) > dom_idx else None
                    seq_info = self._process_anarci_domain(sequences[seq_idx], domain_detail, domain_numbering, domain_hit_table, seq_idx, dom_idx)
                    annotated_sequences.append(seq_info)
            return annotated_sequences
            
        except Exception as e:
            logger.error(f"ANARCI annotation failed: {e}")
            raise RuntimeError(f"ANARCI annotation failed: {e}")

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
        # ANARCI result structure: (numbered, alignment_details, hit_tables)
        numbering = alignment_details = hit_tables = None

        #todo: it seems like anarci returns alignment details for components in the sequence
        # so if there is a coonstant region it will have an alignment detail and if there is a variable region it will have its own alignment detail
        # alignment_details is therefore a list of dictionaries, each with details for a region
        # hit_tables is a list of lists, with different results (e.g. it can give different values for different species)
        # the below code is completely wrong and needs to be fixed
        if isinstance(result, tuple) and len(result) == 3:
            numbering, alignment_details, hit_tables = result
        else:
            numbering = result[0] if isinstance(result, tuple) and len(result) > 0 else result
            alignment_details = None
            hit_tables = None

        seq_info = SequenceInfo(
            sequence=sequence,
            name=f"sequence_{index+1}"
        )

        # Extract chain type and species from alignment_details if available
        if alignment_details and isinstance(alignment_details, dict):
            if 'chain_type' in alignment_details:
                seq_info.chain_type = alignment_details['chain_type']
            if 'species' in alignment_details:
                seq_info.species = alignment_details['species']

        # Extract germline/isotype from hit_tables if present (e.g., with custom HMMs or extended ANARCI)
        if hit_tables and len(hit_tables) > 0:
            best_hit = hit_tables[0]
            if best_hit and len(best_hit) > 0:
                germline_info = best_hit[0]
                if isinstance(germline_info, dict):
                    if 'germline' in germline_info:
                        seq_info.germline = germline_info['germline']
                    if 'isotype' in germline_info:
                        seq_info.isotype = germline_info['isotype']

        # Extract regions (CDR/FR boundaries) if available
        if numbering and isinstance(numbering, dict) and 'regions' in numbering:
            seq_info.regions = numbering['regions']

        return seq_info

    def _process_anarci_domain(self, sequence, domain_detail, numbering, hit_table, seq_idx, dom_idx):
        """
        Process a single ANARCI domain/component and extract relevant information
        """
        from app.models import SequenceInfo
        seq_info = SequenceInfo(
            sequence=sequence,
            name=f"sequence_{seq_idx+1}_domain_{dom_idx+1}"
        )
        if domain_detail:
            seq_info.chain_type = domain_detail.get('chain_type')
            seq_info.species = domain_detail.get('species')
            seq_info.germline = domain_detail.get('id')
            # Optionally, add evalue, bitscore, etc. as custom fields if needed
        if numbering and isinstance(numbering, list):
            # Optionally, parse regions if available (not always present)
            pass
        # Optionally, extract best hit info from hit_table
        if hit_table and isinstance(hit_table, list) and len(hit_table) > 1:
            header = hit_table[0]
            best_hit = hit_table[1]
            if 'id' in header and best_hit:
                idx = header.index('id')
                seq_info.germline = best_hit[idx]
        return seq_info

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
