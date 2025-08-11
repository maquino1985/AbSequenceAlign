"""
Service for creating API responses from annotation results.
Handles conversion between domain entities and API response models.
"""

from typing import Dict, Any, List

from backend.annotation.anarci_result_processor import AnarciResultProcessor
from backend.models.models_v2 import (
    Sequence,
    Chain,
    Domain,
    Region,
    RegionFeature,
    DomainType,
    AnnotationResult,
)
from backend.logger import logger


class AnnotationResponseService:
    """Service for creating API responses from annotation results"""

    def create_api_response_from_processor(
        self, processor: AnarciResultProcessor, numbering_scheme: str
    ) -> AnnotationResult:
        """Convert AnarciResultProcessor results to API response format."""
        sequences = [
            self._create_sequence_from_processor_result(result)
            for result in processor.results
        ]

        return AnnotationResult(
            sequences=sequences,
            numbering_scheme=numbering_scheme,
            total_sequences=len(sequences),
            chain_types=self._calculate_chain_types(processor),
            isotypes=self._calculate_isotypes(processor),
            species=self._calculate_species(processor),
        )

    def process_annotation_request_for_api(
        self, input_dict: Dict[str, Any], numbering_scheme: str
    ) -> AnnotationResult:
        """Process an annotation request and return formatted API response."""
        processor = AnarciResultProcessor(
            input_dict, numbering_scheme=numbering_scheme
        )
        return self.create_api_response_from_processor(
            processor, numbering_scheme
        )

    def _create_sequence_from_processor_result(self, result: Any) -> Sequence:
        """Create a Sequence from a processor result object."""
        chains = [
            self._create_chain_from_processor_chain(chain)
            for chain in result.chains
        ]

        return Sequence(
            name=result.biologic_name,
            original_sequence=(
                result.chains[0].sequence if result.chains else ""
            ),
            chains=chains,
        )

    def _create_chain_from_processor_chain(self, chain: Any) -> Chain:
        """Create a Chain from a processor chain object."""
        domains = [
            self._create_domain_from_processor_domain(domain)
            for domain in chain.domains
        ]

        return Chain(name=chain.name, sequence=chain.sequence, domains=domains)

    def _create_domain_from_processor_domain(self, domain: Any) -> Domain:
        """Create a Domain from a processor domain object."""
        regions = []

        logger.debug(
            f"Processing domain {domain.domain_type} with {len(domain.sequence)} chars"
        )
        logger.debug(f"Domain has regions: {hasattr(domain, 'regions')}")
        if hasattr(domain, "regions"):
            logger.debug(f"Regions data: {domain.regions}")

        if hasattr(domain, "regions") and domain.regions:
            for region_name, region_data in domain.regions.items():
                try:
                    logger.debug(
                        f"Processing region {region_name} with data type {type(region_data)}"
                    )
                    region = self._create_region_from_data(
                        region_name, region_data, domain.sequence
                    )
                    regions.append(region)
                    logger.debug(f"Created region {region_name}")
                except Exception as e:
                    logger.warning(f"Error creating region {region_name}: {e}")
                    region = self._create_fallback_region(
                        region_name, domain.sequence
                    )
                    regions.append(region)

        logger.debug(
            f"Created {len(regions)} regions for domain {domain.domain_type}"
        )
        return Domain(
            domain_type=self._map_domain_type(domain.domain_type),
            start=0,
            stop=len(domain.sequence),
            sequence=domain.sequence,
            regions=regions,
        )

    def _create_region_from_data(
        self, region_name: str, region_data: Any, domain_sequence: str
    ) -> Region:
        """Create a Region from region data."""
        if (
            hasattr(region_data, "start")
            and hasattr(region_data, "stop")
            and hasattr(region_data, "sequence")
        ):
            # AntibodyRegion object
            return Region(
                name=region_name,
                start=region_data.start,
                stop=region_data.stop,
                features=[
                    RegionFeature(kind="sequence", value=region_data.sequence)
                ],
            )
        elif isinstance(region_data, dict):
            # Dictionary with region data
            return Region(
                name=region_name,
                start=region_data.get("start", 0),
                stop=region_data.get("stop", 0),
                features=[
                    RegionFeature(
                        kind="sequence", value=region_data.get("sequence", "")
                    )
                ],
            )
        else:
            return self._create_fallback_region(region_name, domain_sequence)

    def _create_fallback_region(
        self, region_name: str, domain_sequence: str
    ) -> Region:
        """Create a fallback Region when region data is not available."""
        return Region(
            name=region_name,
            start=0,
            stop=len(domain_sequence),
            features=[RegionFeature(kind="sequence", value=domain_sequence)],
        )

    def _map_domain_type(self, domain_type_str: str) -> DomainType:
        """Map domain type string to DomainType enum."""
        domain_type_map = {
            "V": DomainType.VARIABLE,
            "C": DomainType.CONSTANT,
            "LINKER": DomainType.LINKER,
        }
        return domain_type_map.get(domain_type_str, DomainType.VARIABLE)

    def _calculate_chain_types(
        self, processor: AnarciResultProcessor
    ) -> Dict[str, int]:
        """Calculate chain type statistics from processor results."""
        chain_types = {}
        for result in processor.results:
            for chain in result.chains:
                chain_type = chain.name
                chain_types[chain_type] = chain_types.get(chain_type, 0) + 1
        return chain_types

    def _calculate_isotypes(
        self, processor: AnarciResultProcessor
    ) -> Dict[str, int]:
        """Calculate isotype statistics from processor results."""
        isotypes = {}
        for result in processor.results:
            for chain in result.chains:
                for domain in chain.domains:
                    if hasattr(domain, "isotype") and domain.isotype:
                        isotype = domain.isotype
                        isotypes[isotype] = isotypes.get(isotype, 0) + 1
        return isotypes

    def _calculate_species(
        self, processor: AnarciResultProcessor
    ) -> Dict[str, int]:
        """Calculate species statistics from processor results."""
        species = {}
        for result in processor.results:
            for chain in result.chains:
                for domain in chain.domains:
                    if hasattr(domain, "species") and domain.species:
                        species_name = domain.species
                        species[species_name] = (
                            species.get(species_name, 0) + 1
                        )
        return species
