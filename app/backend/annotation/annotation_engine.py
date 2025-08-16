# This file is now deprecated. AnnotationEngine and related logic have been replaced by AnarciResultProcessor and annotate_sequences_with_processor.
# All annotation should use the new pipeline.

from typing import List

# If you need annotation, import annotate_sequences_with_processor from this module.
from .anarci_result_processor import AnarciResultProcessor
from backend.models.models import (
    SequenceInfo,
    AnnotationResult,
    NumberingScheme,
    SequenceInput,
)


def annotate_sequences_with_processor(
    sequences: List[SequenceInput],
    numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
) -> AnnotationResult:
    """
    Annotate sequences using AnarciResultProcessor and return AnnotationResult.
    """
    if not sequences:
        return AnnotationResult(
            sequences=[],
            numbering_scheme=numbering_scheme,
            total_sequences=0,
            chain_types={},
            isotypes={},
            species={},
        )

    # Convert SequenceInput objects to the format expected by AnarciResultProcessor
    # Each sequence becomes {name: {chain_label: sequence_value}}
    input_dict = {}
    for seq in sequences:
        # Get all chains using the new explicit method
        chain_data = seq.get_all_chains()
        if chain_data:  # Only add if there are chains
            input_dict[seq.name] = chain_data

    processor = AnarciResultProcessor(
        input_dict, numbering_scheme=numbering_scheme.value
    )
    all_sequence_infos = []
    chain_types = {}
    isotypes = {}
    species_counts = {}

    for result_obj in processor.results:
        for chain in result_obj.chains:
            # Always use the original FASTA header (biologic_name) as the sequence name
            sequence_name = result_obj.biologic_name

            # Get the primary domain (first variable domain) for chain metadata
            primary_domain = next(
                (d for d in chain.domains if d.domain_type == "V"),
                chain.domains[0],
            )

            # Collect regions from all domains (regions are now absolute positions)
            all_regions = {}
            for i, domain in enumerate(chain.domains):
                if domain.domain_type == "LINKER":
                    # Create a region for the linker
                    all_regions[f"LINKER_{i}"] = {
                        "name": "LINKER",
                        "start": domain.alignment_details["start"],
                        "stop": domain.alignment_details["end"],
                        "sequence": domain.sequence,
                        "domain_type": "LINKER",
                    }
                elif domain.domain_type == "V" and hasattr(domain, "regions"):
                    # Keep original region names; positions are absolute now
                    for region_name, region_data in domain.regions.items():
                        all_regions[region_name] = region_data

            # Create a single SequenceInfo for the entire chain
            info = SequenceInfo(
                sequence=chain.sequence,  # Use full chain sequence
                name=sequence_name,
                chain_type=primary_domain.isotype,  # Use primary domain's isotype
                isotype=primary_domain.isotype,
                species=primary_domain.species,
                germline=(
                    str(primary_domain.germlines)
                    if primary_domain.germlines is not None
                    else None
                ),
                regions=all_regions,
            )
            all_sequence_infos.append(info)

            # Stats - only count primary domain
            if primary_domain.isotype:
                chain_types[primary_domain.isotype] = (
                    chain_types.get(primary_domain.isotype, 0) + 1
                )
                isotypes[primary_domain.isotype] = (
                    isotypes.get(primary_domain.isotype, 0) + 1
                )
            if primary_domain.species:
                species_counts[primary_domain.species] = (
                    species_counts.get(primary_domain.species, 0) + 1
                )

    return AnnotationResult(
        sequences=all_sequence_infos,
        numbering_scheme=numbering_scheme,
        total_sequences=len(all_sequence_infos),
        chain_types=chain_types,
        isotypes=isotypes,
        species=species_counts,
    )
