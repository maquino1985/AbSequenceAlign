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
from backend.logger import logger


class AnnotationService(AbstractProcessingSubject):
    """Service for orchestrating antibody sequence annotation"""

    def __init__(self):
        super().__init__()
        self._anarci_adapter = AnarciAdapter()
        self._hmmer_adapter = HmmerAdapter()

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
