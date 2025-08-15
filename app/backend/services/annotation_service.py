from typing import Dict, List, Tuple

from backend.annotation.AnarciResultProcessor import AnarciResultProcessor
from backend.models.models_v2 import (
    AnnotationResult as V2AnnotationResult,
    Sequence as V2Sequence,
    Chain as V2Chain,
    Domain as V2Domain,
    Region as V2Region,
    RegionFeature as V2RegionFeature,
    DomainType,
)
from backend.models.requests_v2 import AnnotationRequestV2


class AnnotationService:
    @staticmethod
    def _map_domain_type(domain_type: str) -> DomainType:
        """Map raw domain type to DomainType enum."""
        if domain_type == "C":
            return DomainType.CONSTANT
        elif domain_type == "LINKER":
            return DomainType.LINKER
        return DomainType.VARIABLE

    @staticmethod
    def _get_domain_positions(domain, domain_type: DomainType) -> tuple[int, int]:
        """Extract start and stop positions from domain."""
        if not domain.alignment_details:
            return None, None

        if domain_type == DomainType.LINKER:
            return (
                domain.alignment_details.get("start"),
                domain.alignment_details.get("end")
            )
        return (
            domain.alignment_details.get("query_start"),
            domain.alignment_details.get("query_end")
        )

    @staticmethod
    def _process_region(region) -> tuple[int, int, str]:
        """Process a region and return its start, stop, and sequence."""
        if isinstance(region, dict):
            start = int(region.get("start")) + 1  # Convert to 1-based
            stop = int(region.get("stop")) + 1    # Convert to 1-based
            sequence = region.get("sequence")
        else:
            start = int(region.start) + 1         # Convert to 1-based
            stop = int(region.stop) + 1           # Convert to 1-based
            sequence = region.sequence
        return start, stop, sequence

    def _process_regions(self, domain) -> List[V2Region]:
        """Process all regions in a domain."""
        if not hasattr(domain, "regions") or not domain.regions:
            return []

        regions = []
        for name, region in domain.regions.items():
            start, stop, sequence = self._process_region(region)
            regions.append(self._create_v2_region(name, start, stop, sequence))
        return regions

    @staticmethod
    def _create_v2_region(name: str, start: int, stop: int, sequence: str) -> V2Region:
        """Create a V2Region object with features."""
        features = [V2RegionFeature(kind="sequence", value=sequence)]
        return V2Region(
            name=name,
            start=start,
            stop=stop,
            features=features,
        )

    def _process_domain(self, domain) -> V2Domain:
        """Process a single domain and return V2Domain object."""
        domain_type = self._map_domain_type(getattr(domain, "domain_type", "V"))
        start, stop = self._get_domain_positions(domain, domain_type)
        regions = self._process_regions(domain)

        return V2Domain(
            domain_type=domain_type,
            start=start,
            stop=stop,
            sequence=domain.sequence,
            regions=regions,
            isotype=getattr(domain, "isotype", None),
            species=getattr(domain, "species", None),
            metadata={},
        )

    def _process_chain(self, chain) -> V2Chain:
        """Process a single chain and return V2Chain object."""
        domains = [self._process_domain(domain) for domain in chain.domains]
        return V2Chain(
            name=chain.name,
            sequence=chain.sequence,
            domains=domains,
        )

    def _process_sequence(self, result) -> V2Sequence:
        """Process a single sequence result and return V2Sequence object."""
        chains = [self._process_chain(chain) for chain in result.chains]
        return V2Sequence(
            name=result.biologic_name,
            original_sequence=chains[0].sequence if chains else "",
            chains=chains,
        )

    @staticmethod
    def _calculate_statistics(processor: AnarciResultProcessor) -> Tuple[Dict, Dict, Dict]:
        """Calculate statistics from processor results."""
        chain_types = {}
        isotypes = {}
        species_counts = {}

        for result in processor.results:
            for chain in result.chains:
                # Get the primary domain (first variable domain) for chain metadata
                primary_domain = next(
                    (d for d in chain.domains if d.domain_type == "V"),
                    chain.domains[0],
                )

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

        return chain_types, isotypes, species_counts

    def _prepare_input_dict(self, request: AnnotationRequestV2) -> Dict[str, Dict]:
        """Prepare input dictionary from request sequences."""
        input_dict = {}
        for seq in request.sequences:
            chains = seq.get_all_chains()
            if chains:
                input_dict[seq.name] = chains
        return input_dict

    def process_annotation_request(self, request: AnnotationRequestV2) -> V2AnnotationResult:
        """Process an annotation request and return V2AnnotationResult."""
        # Prepare input and create processor
        input_dict = self._prepare_input_dict(request)
        processor = AnarciResultProcessor(
            input_dict, numbering_scheme=request.numbering_scheme.value
        )

        # Process sequences
        sequences = [self._process_sequence(result) for result in processor.results]

        # Calculate statistics
        chain_types, isotypes, species_counts = self._calculate_statistics(processor)

        # Create and return result
        return V2AnnotationResult(
            sequences=sequences,
            numbering_scheme=request.numbering_scheme.value,
            total_sequences=len(sequences),
            chain_types=chain_types,
            isotypes=isotypes,
            species=species_counts,
        )