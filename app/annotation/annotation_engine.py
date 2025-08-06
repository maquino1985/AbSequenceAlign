# This file is now deprecated. AnnotationEngine and related logic have been replaced by AnarciResultProcessor and annotate_sequences_with_processor.
# All annotation should use the new pipeline.

# If you need annotation, import annotate_sequences_with_processor from this module.
from app.annotation.AnarciResultProcessor import AnarciResultProcessor
from app.models.models import SequenceInfo, AnnotationResult, NumberingScheme
from typing import List


def annotate_sequences_with_processor(
        sequences: List[str],
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT
) -> AnnotationResult:
    """
    Annotate sequences using AnarciResultProcessor and return AnnotationResult.
    """
    if not sequences:
        return AnnotationResult(sequences=[], numbering_scheme=numbering_scheme, total_sequences=0, chain_types={},
                                isotypes={}, species={})
    # Prepare input dict for AnarciResultProcessor
    input_dict = {f"seq_{i + 1}": {f"chain_{i + 1}": seq} for i, seq in enumerate(sequences)}
    processor = AnarciResultProcessor(input_dict, numbering_scheme=numbering_scheme.value)
    all_sequence_infos = []
    chain_types = {}
    isotypes = {}
    species_counts = {}
    for result_obj in processor.results:
        for chain in result_obj.chains:
            for domain in chain.domains:
                info = SequenceInfo(
                    sequence=domain.sequence,
                    name=chain.name,
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
