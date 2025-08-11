"""
Annotation service for orchestrating antibody sequence annotation.
Implements the Strategy pattern for different annotation approaches.
"""

from typing import Dict, Any, List, Optional

from backend.core.base_classes import AbstractProcessingSubject
from backend.core.interfaces import ProcessingResult
from backend.core.exceptions import AnnotationError, ValidationError
from backend.domain.models import (
    NumberingScheme,
    ChainType,
    DomainType,
    RegionType,
)
from backend.domain.entities import (
    AntibodySequence,
    AntibodyChain,
    AntibodyDomain,
    AntibodyRegion,
)
from backend.domain.value_objects import (
    RegionBoundary,
)
from backend.infrastructure.adapters.anarci_adapter import AnarciAdapter
from backend.infrastructure.adapters.hmmer_adapter import HmmerAdapter
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
from backend.application.services.biologic_service import BiologicService
from backend.logger import logger


class AnnotationService(AbstractProcessingSubject):
    """Service for orchestrating antibody sequence annotation"""

    def __init__(self):
        super().__init__()
        self._anarci_adapter = AnarciAdapter()
        self._hmmer_adapter = HmmerAdapter()
        self._biologic_service = BiologicService()

    def process_sequence(
        self,
        sequence: AntibodySequence,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> ProcessingResult:
        """Process a sequence through annotation (alias for annotate_sequence)"""
        return self.annotate_sequence(sequence, numbering_scheme)

    def annotate_sequence(
        self,
        sequence: AntibodySequence,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> ProcessingResult:
        """Annotate a complete antibody sequence"""
        try:
            logger.info(f"Starting annotation for sequence: {sequence.name}")
            self.notify_step_completed("start", 0.0)

            # Validate sequence
            if not self._validate_sequence(sequence):
                raise ValidationError(
                    "Invalid antibody sequence", field="sequence"
                )

            # Process each chain
            annotated_chains = []
            total_chains = len(sequence.chains)

            for i, chain in enumerate(sequence.chains):
                logger.debug(
                    f"Processing chain {i+1}/{total_chains}: {chain.name}"
                )
                progress = (
                    i / total_chains
                ) * 0.8  # 80% of work is chain processing
                self.notify_step_completed(f"chain_{i+1}", progress)

                annotated_chain = self.annotate_chain(chain, numbering_scheme)
                annotated_chains.append(annotated_chain)

            # Create annotated sequence
            annotated_sequence = AntibodySequence(
                name=sequence.name,
                chains=annotated_chains,
                metadata=sequence.metadata,
            )

            self.notify_step_completed("complete", 1.0)
            logger.info(f"Annotation completed for sequence: {sequence.name}")

            return ProcessingResult(
                success=True,
                data={"annotated_sequence": annotated_sequence},
                metadata={"chains_processed": total_chains},
            )

        except Exception as e:
            error_msg = (
                f"Annotation failed for sequence {sequence.name}: {str(e)}"
            )
            logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def annotate_chain(
        self,
        chain: AntibodyChain,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> AntibodyChain:
        """Annotate a single antibody chain"""
        try:
            logger.debug(f"Annotating chain: {chain.name}")

            # Validate chain
            if not self._validate_chain(chain):
                raise ValidationError("Invalid antibody chain", field="chain")

            # Detect chain type if not specified
            if not chain.chain_type:
                chain.chain_type = self._detect_chain_type(chain)

            # Process domains
            annotated_domains = []
            for domain in chain.domains:
                annotated_domain = self.annotate_domain(
                    domain, numbering_scheme
                )
                annotated_domains.append(annotated_domain)

            # Create annotated chain
            annotated_chain = AntibodyChain(
                name=chain.name,
                chain_type=chain.chain_type,
                sequence=chain.sequence,
                domains=annotated_domains,
                metadata=chain.metadata,
            )

            return annotated_chain

        except Exception as e:
            raise AnnotationError(
                f"Chain annotation failed: {str(e)}", step="chain_annotation"
            )

    def annotate_domain(
        self,
        domain: AntibodyDomain,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> AntibodyDomain:
        """Annotate a single antibody domain"""
        try:
            logger.debug(f"Annotating domain: {domain.domain_type}")

            if domain.domain_type == DomainType.VARIABLE:
                return self._annotate_variable_domain(domain, numbering_scheme)
            elif domain.domain_type == DomainType.CONSTANT:
                return self._annotate_constant_domain(domain)
            elif domain.domain_type == DomainType.LINKER:
                return self._annotate_linker_domain(domain)
            else:
                raise AnnotationError(
                    f"Unknown domain type: {domain.domain_type}"
                )

        except Exception as e:
            raise AnnotationError(
                f"Domain annotation failed: {str(e)}", step="domain_annotation"
            )

    def _annotate_variable_domain(
        self, domain: AntibodyDomain, numbering_scheme: NumberingScheme
    ) -> AntibodyDomain:
        """Annotate a variable domain using ANARCI"""
        try:
            # Use ANARCI for numbering and region annotation
            anarci_result = self._anarci_adapter.number_sequence(
                str(domain.sequence), scheme=numbering_scheme
            )

            if not anarci_result.get("success", False):
                raise AnnotationError(
                    "ANARCI numbering failed", step="anarci_numbering"
                )

            # Extract regions from ANARCI result
            regions = self._extract_regions_from_anarci(anarci_result, domain)

            # Create annotated domain
            annotated_domain = AntibodyDomain(
                domain_type=domain.domain_type,
                sequence=domain.sequence,
                numbering_scheme=numbering_scheme,
                regions=regions,
                metadata={**domain.metadata, "anarci_result": anarci_result},
            )

            return annotated_domain

        except Exception as e:
            raise AnnotationError(
                f"Variable domain annotation failed: {str(e)}",
                step="variable_domain",
            )

    def _annotate_constant_domain(
        self, domain: AntibodyDomain
    ) -> AntibodyDomain:
        """Annotate a constant domain using HMMER"""
        try:
            # Use HMMER for isotype detection
            hmmer_result = self._hmmer_adapter.detect_isotype(
                str(domain.sequence)
            )

            if not hmmer_result.get("success", False):
                raise AnnotationError(
                    "HMMER isotype detection failed", step="hmmer_detection"
                )

            # Create constant region
            constant_region = AntibodyRegion(
                name="CONSTANT",
                region_type=RegionType.CONSTANT,
                boundary=self._calculate_constant_boundary(domain),
                sequence=domain.sequence,
                numbering_scheme=domain.numbering_scheme,
            )

            # Create annotated domain
            annotated_domain = AntibodyDomain(
                domain_type=domain.domain_type,
                sequence=domain.sequence,
                numbering_scheme=domain.numbering_scheme,
                regions={"CONSTANT": constant_region},
                metadata={
                    **domain.metadata,
                    "hmmer_result": hmmer_result,
                    "isotype": hmmer_result.get("data", {}).get(
                        "best_isotype"
                    ),
                },
            )

            return annotated_domain

        except Exception as e:
            raise AnnotationError(
                f"Constant domain annotation failed: {str(e)}",
                step="constant_domain",
            )

    def _annotate_linker_domain(
        self, domain: AntibodyDomain
    ) -> AntibodyDomain:
        """Annotate a linker domain"""
        try:
            # Create linker region
            linker_region = AntibodyRegion(
                name="LINKER",
                region_type=RegionType.LINKER,
                boundary=self._calculate_linker_boundary(domain),
                sequence=domain.sequence,
                numbering_scheme=domain.numbering_scheme,
            )

            # Create annotated domain
            annotated_domain = AntibodyDomain(
                domain_type=domain.domain_type,
                sequence=domain.sequence,
                numbering_scheme=domain.numbering_scheme,
                regions={"LINKER": linker_region},
                metadata=domain.metadata,
            )

            return annotated_domain

        except Exception as e:
            raise AnnotationError(
                f"Linker domain annotation failed: {str(e)}",
                step="linker_domain",
            )

    def _extract_regions_from_anarci(
        self, anarci_result: Dict[str, Any], domain: AntibodyDomain
    ) -> Dict[str, AntibodyRegion]:
        """Extract regions from ANARCI result"""
        regions = {}

        try:
            # Get the first result (single sequence)
            result = anarci_result.get("data", {}).get("results", [{}])[0]
            numbered = result.get("numbered", [])

            if not numbered:
                return regions

            # Extract CDR and FR regions based on numbering scheme
            regions.update(self._extract_cdr_regions(numbered, domain))
            regions.update(self._extract_fr_regions(numbered, domain))

        except Exception as e:
            logger.warning(f"Failed to extract regions from ANARCI: {e}")

        return regions

    def _extract_cdr_regions(
        self, numbered: List, domain: AntibodyDomain
    ) -> Dict[str, AntibodyRegion]:
        """Extract CDR regions from numbered sequence"""
        regions = {}

        # CDR boundaries based on IMGT numbering (simplified)
        cdr_boundaries = {
            "CDR1": (27, 38),
            "CDR2": (56, 65),
            "CDR3": (105, 117),
        }

        for cdr_name, (start, end) in cdr_boundaries.items():
            try:
                # Extract CDR sequence
                cdr_sequence = self._extract_region_sequence(
                    numbered, start, end
                )
                if cdr_sequence:
                    region = AntibodyRegion(
                        name=cdr_name,
                        region_type=getattr(RegionType, cdr_name),
                        boundary=self._create_boundary(start, end),
                        sequence=domain.sequence,  # Use domain sequence for now
                        numbering_scheme=domain.numbering_scheme,
                    )
                    regions[cdr_name] = region
            except Exception as e:
                logger.warning(f"Failed to extract {cdr_name}: {e}")

        return regions

    def _extract_fr_regions(
        self, numbered: List, domain: AntibodyDomain
    ) -> Dict[str, AntibodyRegion]:
        """Extract FR regions from numbered sequence"""
        regions = {}

        # FR boundaries based on IMGT numbering (simplified)
        fr_boundaries = {
            "FR1": (1, 26),
            "FR2": (39, 55),
            "FR3": (66, 104),
            "FR4": (118, 128),
        }

        for fr_name, (start, end) in fr_boundaries.items():
            try:
                # Extract FR sequence
                fr_sequence = self._extract_region_sequence(
                    numbered, start, end
                )
                if fr_sequence:
                    region = AntibodyRegion(
                        name=fr_name,
                        region_type=getattr(RegionType, fr_name),
                        boundary=self._create_boundary(start, end),
                        sequence=domain.sequence,  # Use domain sequence for now
                        numbering_scheme=domain.numbering_scheme,
                    )
                    regions[fr_name] = region
            except Exception as e:
                logger.warning(f"Failed to extract {fr_name}: {e}")

        return regions

    def _extract_region_sequence(
        self, numbered: List, start: int, end: int
    ) -> Optional[str]:
        """Extract sequence for a specific region"""
        try:
            region_sequence = ""
            for position, amino_acid in numbered:
                if isinstance(position, (list, tuple)):
                    pos_num = position[0]
                else:
                    pos_num = position

                if start <= pos_num <= end and amino_acid != "-":
                    region_sequence += amino_acid

            return region_sequence if region_sequence else None
        except Exception:
            return None

    def _create_boundary(self, start: int, end: int) -> RegionBoundary:
        """Create a region boundary"""
        return RegionBoundary(start, end)

    def _calculate_constant_boundary(self, domain: AntibodyDomain):
        """Calculate boundary for constant region"""
        return self._create_boundary(0, len(domain.sequence) - 1)

    def _calculate_linker_boundary(self, domain: AntibodyDomain):
        """Calculate boundary for linker region"""
        return self._create_boundary(0, len(domain.sequence) - 1)

    def _detect_chain_type(self, chain: AntibodyChain) -> ChainType:
        """Detect chain type based on sequence characteristics"""
        # Simplified chain type detection
        sequence = str(chain.sequence).upper()

        # Check for heavy chain characteristics
        if "IGH" in sequence or len(sequence) > 400:
            return ChainType.HEAVY

        # Check for light chain characteristics
        if "IGK" in sequence or "IGL" in sequence:
            return ChainType.LIGHT

        # Default to light chain
        return ChainType.LIGHT

    def _validate_sequence(self, sequence: AntibodySequence) -> bool:
        """Validate antibody sequence"""
        if not sequence or not sequence.name:
            return False

        if not sequence.chains:
            return False

        return True

    def _validate_chain(self, chain: AntibodyChain) -> bool:
        """Validate antibody chain"""
        if not chain or not chain.name:
            return False

        if not chain.sequence:
            return False

        return True

    # =============================================================================
    # API Response Formatting Methods
    # =============================================================================

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

    # =============================================================================
    # Integration with Biologic Models for Persistence
    # =============================================================================

    async def annotate_and_persist_sequence(
        self,
        db_session,
        input_dict: Dict[str, Any],
        numbering_scheme: str = "imgt",
        organism: Optional[str] = None
    ):
        """
        Annotate a sequence and persist it as a biologic entity.
        
        This method demonstrates the integration pattern:
        1. Use domain entities for annotation (business logic)
        2. Convert to ORM models for persistence
        3. Return Pydantic models for API responses
        """
        # Step 1: Process with AnarciResultProcessor (existing logic)
        processor = AnarciResultProcessor(input_dict, numbering_scheme=numbering_scheme)
        
        # Step 2: Convert processor results to domain entities
        antibody_sequence = self._create_antibody_sequence_from_processor(processor)
        
        # Step 3: Use biologic service to persist as ORM models
        biologic_response = await self._biologic_service.process_and_persist_antibody_sequence(
            db_session, antibody_sequence, organism
        )
        
        # Step 4: Return both the biologic response and the original annotation result
        annotation_result = self.create_api_response_from_processor(processor, numbering_scheme)
        
        return {
            "biologic": biologic_response,
            "annotation": annotation_result
        }

    def _create_antibody_sequence_from_processor(
        self, processor: AnarciResultProcessor
    ) -> AntibodySequence:
        """
        Create an AntibodySequence domain entity from AnarciResultProcessor results.
        
        This bridges the gap between the processor results and domain entities.
        """
        from backend.domain.value_objects import AminoAcidSequence
        from backend.domain.models import ChainType, DomainType, RegionType, NumberingScheme
        
        chains = []
        
        for result in processor.results:
            for chain_data in result.chains:
                # Create domains for this chain
                domains = []
                for domain_data in chain_data.domains:
                    # Create regions for this domain
                    regions = {}
                    if hasattr(domain_data, "regions") and domain_data.regions:
                        for region_name, region_data in domain_data.regions.items():
                            try:
                                region = self._create_antibody_region_from_processor_data(
                                    region_name, region_data, domain_data.sequence
                                )
                                regions[region_name] = region
                            except Exception as e:
                                logger.warning(f"Error creating region {region_name}: {e}")
                                # Create fallback region
                                region = self._create_fallback_antibody_region(
                                    region_name, domain_data.sequence
                                )
                                regions[region_name] = region
                    
                    # Create domain
                    domain = AntibodyDomain(
                        domain_type=DomainType(domain_data.domain_type.upper()),
                        sequence=AminoAcidSequence(domain_data.sequence),
                        numbering_scheme=NumberingScheme.IMGT,
                        regions=regions,
                        metadata={}
                    )
                    domains.append(domain)
                
                # Create chain
                chain = AntibodyChain(
                    name=chain_data.name,
                    chain_type=ChainType(chain_data.chain_type.upper()),
                    sequence=AminoAcidSequence(chain_data.sequence),
                    domains=domains,
                    metadata={}
                )
                chains.append(chain)
        
        # Create antibody sequence
        sequence_name = processor.results[0].biologic_name if processor.results else "Unknown"
        return AntibodySequence(
            name=sequence_name,
            chains=chains,
            metadata={}
        )

    def _create_antibody_region_from_processor_data(
        self, region_name: str, region_data: Any, domain_sequence: str
    ) -> AntibodyRegion:
        """Create an AntibodyRegion domain entity from processor data."""
        from backend.domain.value_objects import AminoAcidSequence, RegionBoundary, ConfidenceScore
        from backend.domain.models import RegionType, NumberingScheme
        
        # Extract region boundaries
        start = getattr(region_data, "start", 0)
        end = getattr(region_data, "end", len(domain_sequence) - 1)
        
        # Create boundary
        boundary = RegionBoundary(start=start, end=end)
        
        # Extract sequence
        sequence = getattr(region_data, "sequence", domain_sequence[start:end+1])
        amino_acid_sequence = AminoAcidSequence(sequence)
        
        # Determine region type
        region_type = self._map_region_type(region_name)
        
        # Create confidence score if available
        confidence_score = None
        if hasattr(region_data, "confidence"):
            confidence_score = ConfidenceScore(region_data.confidence)
        
        return AntibodyRegion(
            name=region_name,
            region_type=region_type,
            boundary=boundary,
            sequence=amino_acid_sequence,
            numbering_scheme=NumberingScheme.IMGT,
            metadata={},
            confidence_score=confidence_score
        )

    def _create_fallback_antibody_region(
        self, region_name: str, domain_sequence: str
    ) -> AntibodyRegion:
        """Create a fallback AntibodyRegion when processor data is incomplete."""
        from backend.domain.value_objects import AminoAcidSequence, RegionBoundary
        from backend.domain.models import RegionType, NumberingScheme
        
        # Create a simple region covering the entire domain
        boundary = RegionBoundary(start=0, end=len(domain_sequence) - 1)
        sequence = AminoAcidSequence(domain_sequence)
        region_type = self._map_region_type(region_name)
        
        return AntibodyRegion(
            name=region_name,
            region_type=region_type,
            boundary=boundary,
            sequence=sequence,
            numbering_scheme=NumberingScheme.IMGT,
            metadata={"fallback": True},
            confidence_score=None
        )

    def _map_region_type(self, region_name: str) -> RegionType:
        """Map region name to RegionType enum."""
        from backend.domain.models import RegionType
        
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
