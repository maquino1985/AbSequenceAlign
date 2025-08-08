# This file is now deprecated. AnnotationEngine and related logic have been replaced by AnarciResultProcessor and annotate_sequences_with_processor.
# All annotation should use the new pipeline.

# If you need annotation, import annotate_sequences_with_processor from this module.
from .AnarciResultProcessor import AnarciResultProcessor
from ..models.models import SequenceInfo, AnnotationResult, NumberingScheme, SequenceInput
from typing import List


def annotate_sequences_with_processor(
        sequences: List[SequenceInput],
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT
) -> AnnotationResult:
    """
    Annotate sequences using AnarciResultProcessor and return AnnotationResult.
    """
    if not sequences:
        return AnnotationResult(sequences=[], numbering_scheme=numbering_scheme, total_sequences=0, chain_types={},
                                isotypes={}, species={})
    
    # Convert SequenceInput objects to the format expected by AnarciResultProcessor
    # Each sequence becomes {name: {chain_label: sequence_value}}
    input_dict = {}
    for seq in sequences:
        # Get all chains using the new explicit method
        chain_data = seq.get_all_chains()
        if chain_data:  # Only add if there are chains
            input_dict[seq.name] = chain_data
    
    processor = AnarciResultProcessor(input_dict, numbering_scheme=numbering_scheme.value)
    all_sequence_infos = []
    chain_types = {}
    isotypes = {}
    species_counts = {}
    
    for result_obj in processor.results:
        for chain in result_obj.chains:
            for domain in chain.domains:
                # Always use the original FASTA header (biologic_name) as the sequence name
                # This preserves the user's original sequence identifiers
                sequence_name = result_obj.biologic_name
                
                info = SequenceInfo(
                    sequence=domain.sequence,
                    name=sequence_name,
                    chain_type=domain.isotype,
                    isotype=domain.isotype,
                    species=domain.species,
                    germline=str(domain.germlines) if domain.germlines is not None else None,
                    regions=getattr(domain, 'regions', None)
                )
                all_sequence_infos.append(info)
                # Stats
                if domain.isotype:
                    chain_types[domain.isotype] = chain_types.get(domain.isotype, 0) + 1
                if domain.isotype:
                    isotypes[domain.isotype] = isotypes.get(domain.isotype, 0) + 1
                if domain.species:
                    species_counts[domain.species] = species_counts.get(domain.species, 0) + 1
    
    return AnnotationResult(
        sequences=all_sequence_infos,
        numbering_scheme=numbering_scheme,
        total_sequences=len(all_sequence_infos),
        chain_types=chain_types,
        isotypes=isotypes,
        species=species_counts
    )
