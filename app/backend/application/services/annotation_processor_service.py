"""
Service for handling processor integration and conversion.
Bridges the gap between processor results and domain entities.
"""

from backend.annotation.anarci_result_processor import AnarciResultProcessor
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
    BiologicDomain,
    BiologicFeature,
)
    ChainType,
    DomainType,
    RegionType,
    NumberingScheme,
)
from backend.logger import logger


class AnnotationProcessorService:
    """Service for handling processor integration and conversion"""

    def create_biologic_entity_from_processor(
        self, processor: AnarciResultProcessor
    ) -> BiologicEntity:
        """
        Create a BiologicEntity domain entity from AnarciResultProcessor results.

        This bridges the gap between the processor results and domain entities.
        """
        chains = []

        for result in processor.results:
            for chain_data in result.chains:
                # Create domains for this chain
                domains = []
                for domain_data in chain_data.domains:
                    # Create regions for this domain
                    regions = {}
                    if hasattr(domain_data, "regions") and domain_data.regions:
                        for (
                            region_name,
                            region_data,
                        ) in domain_data.regions.items():
                            try:
                                region = self._create_biologic_feature_from_processor_data(
                                    region_name,
                                    region_data,
                                    domain_data.sequence,
                                )
                                regions[region_name] = region
                            except Exception as e:
                                logger.warning(
                                    f"Error creating region {region_name}: {e}"
                                )
                                # Create fallback region
                                region = self._create_fallback_biologic_feature(
                                    region_name, domain_data.sequence
                                )
                                regions[region_name] = region

                    # Create domain
                    domain = BiologicDomain(
                        domain_type=DomainType(
                            domain_data.domain_type.upper()
                        ),
                        start_position=0,
                        end_position=len(domain_data.sequence) - 1,
                        confidence_score=1.0,
                        metadata={
                            "sequence": domain_data.sequence,
                            "regions": regions,
                        },
                    )
                    domains.append(domain)

                # Determine chain type based on name
                chain_type = self._detect_chain_type_from_name(chain_data.name)

                # Create sequence with domains
                sequence = BiologicSequence(
                    sequence_type="PROTEIN",
                    sequence_data=chain_data.sequence,
                    domains=domains,
                )

                # Create chain
                chain = BiologicChain(
                    name=chain_data.name,
                    chain_type=chain_type,
                    sequences=[sequence],
                )
                chains.append(chain)

        # Create biologic entity
        sequence_name = (
            processor.results[0].biologic_name
            if processor.results
            else "Unknown"
        )
        return BiologicEntity(
            name=sequence_name,
            biologic_type="antibody",
            chains=chains,
        )

    def _create_biologic_feature_from_processor_data(
        self, region_name: str, region_data: Any, domain_sequence: str
    ) -> BiologicFeature:
        """Create a BiologicFeature domain entity from processor data."""
        # Extract region boundaries
        start = getattr(region_data, "start", 0)
        end = getattr(region_data, "end", len(domain_sequence) - 1)

        # Extract sequence
        sequence = getattr(
            region_data, "sequence", domain_sequence[start : end + 1]
        )

        # Determine region type
        region_type = self._map_region_type(region_name)

        # Create confidence score if available
        confidence_score = 1.0
        if hasattr(region_data, "confidence"):
            confidence_score = region_data.confidence

        return BiologicFeature(
            feature_type=region_name,
            name=region_name,
            value=sequence,
            start_position=start,
            end_position=end,
            confidence_score=confidence_score,
            metadata={"source": "processor"},
        )

    def _create_fallback_biologic_feature(
        self, region_name: str, domain_sequence: str
    ) -> BiologicFeature:
        """Create a fallback BiologicFeature when processor data is incomplete."""
        # Create a simple region covering the entire domain
        region_type = self._map_region_type(region_name)

        return BiologicFeature(
            feature_type=region_name,
            name=region_name,
            value=domain_sequence,
            start_position=0,
            end_position=len(domain_sequence) - 1,
            confidence_score=0.5,  # Lower confidence for fallback
            metadata={"fallback": True, "source": "processor"},
        )

    def _detect_chain_type_from_name(self, chain_name: str) -> ChainType:
        """Detect chain type from chain name."""
        chain_name_lower = chain_name.lower()
        
        if any(keyword in chain_name_lower for keyword in ["heavy", "h", "vh"]):
            return ChainType.HEAVY
        elif any(keyword in chain_name_lower for keyword in ["light", "l", "vl", "kappa", "lambda"]):
            return ChainType.LIGHT
        elif any(keyword in chain_name_lower for keyword in ["scfv", "single"]):
            return ChainType.SCFV
        else:
            # Default to HEAVY if we can't determine
            return ChainType.HEAVY

    def _map_region_type(self, region_name: str) -> RegionType:
        """Map region name to RegionType enum."""
        region_name_lower = region_name.lower()

        if "cdr" in region_name_lower:
            if "1" in region_name_lower:
                return RegionType.CDR1
            elif "2" in region_name_lower:
                return RegionType.CDR2
            elif "3" in region_name_lower:
                return RegionType.CDR3
            else:
                return RegionType.CDR1  # Default
        elif "fr" in region_name_lower:
            if "1" in region_name_lower:
                return RegionType.FR1
            elif "2" in region_name_lower:
                return RegionType.FR2
            elif "3" in region_name_lower:
                return RegionType.FR3
            elif "4" in region_name_lower:
                return RegionType.FR4
            else:
                return RegionType.FR1  # Default
        else:
            return RegionType.FR1  # Default fallback
