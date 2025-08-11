"""
Annotation service for orchestrating biologic sequence annotation.
Focuses on domain annotation logic only.
"""

from typing import Dict, Any, List, Optional

from backend.core.base_classes import AbstractProcessingSubject
from backend.core.interfaces import (
    ProcessingResult,
    AnnotationService as IAnnotationService,
)
from backend.core.exceptions import AnnotationError, ValidationError
from backend.domain.models import (
    NumberingScheme,
    ChainType,
    DomainType,
    RegionType,
)
from backend.domain.entities import (
    BiologicEntity,
    BiologicChain,
    BiologicSequence,
    BiologicDomain,
    BiologicFeature,
)
from backend.domain.value_objects import (
    RegionBoundary,
)
from backend.infrastructure.adapters.anarci_adapter import AnarciAdapter
from backend.infrastructure.adapters.hmmer_adapter import HmmerAdapter
from backend.utils.validation_utils import ValidationUtils
from backend.logger import logger


class AnnotationService(AbstractProcessingSubject, IAnnotationService):
    """Service for orchestrating biologic sequence annotation"""

    def __init__(self):
        super().__init__()
        self._anarci_adapter = AnarciAdapter()
        self._hmmer_adapter = HmmerAdapter()

    def process_sequence(
        self,
        sequence: BiologicEntity,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> ProcessingResult:
        """Process a sequence through annotation (alias for annotate_sequence)"""
        return self.annotate_sequence(sequence, numbering_scheme)

    def annotate_sequence(
        self,
        sequence: BiologicEntity,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> ProcessingResult:
        """Annotate a complete biologic sequence"""
        try:
            logger.info(f"Starting annotation for sequence: {sequence.name}")
            self.notify_step_completed("start", 0.0)

            # Validate sequence
            if not ValidationUtils.validate_sequence(sequence):
                raise ValidationError(
                    "Invalid biologic sequence", field="sequence"
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
            annotated_sequence = BiologicEntity(
                name=sequence.name,
                biologic_type=sequence.biologic_type,
                chains=annotated_chains,
                metadata=sequence.metadata,
            )

            self.notify_step_completed("complete", 1.0)
            return ProcessingResult(
                success=True,
                data=annotated_sequence,
                message=f"Successfully annotated sequence: {sequence.name}",
            )

        except Exception as e:
            self.notify_processing_failed(str(e))
            logger.error(f"Error annotating sequence: {e}")
            raise AnnotationError(
                f"Sequence annotation failed: {str(e)}",
                step="sequence_annotation",
            )

    def annotate_chain(
        self,
        chain: BiologicChain,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> BiologicChain:
        """Annotate a single biologic chain"""
        try:
            logger.debug(f"Annotating chain: {chain.name}")

            # Detect chain type if not specified
            if not chain.chain_type:
                chain.chain_type = self._detect_chain_type(chain)

            # Process domains from sequences
            annotated_sequences = []
            for sequence in chain.sequences:
                # Annotate domains in this sequence
                annotated_domains = []
                for domain in sequence.domains:
                    if domain.domain_type == DomainType.VARIABLE:
                        annotated_domain = self._annotate_variable_domain(
                            domain, numbering_scheme
                        )
                    elif domain.domain_type == DomainType.CONSTANT:
                        annotated_domain = self._annotate_constant_domain(
                            domain
                        )
                    elif domain.domain_type == DomainType.LINKER:
                        annotated_domain = self._annotate_linker_domain(domain)
                    else:
                        raise AnnotationError(
                            f"Unknown domain type: {domain.domain_type}",
                            step="domain_type_check",
                        )
                    annotated_domains.append(annotated_domain)
                sequence.domains = annotated_domains
                annotated_sequences.append(sequence)
            chain.sequences = annotated_sequences

            return chain

        except AnnotationError:
            raise
        except Exception as e:
            raise AnnotationError(
                f"Chain annotation failed: {str(e)}", step="chain_annotation"
            )

    def annotate_domain(
        self,
        domain: BiologicDomain,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
    ) -> BiologicDomain:
        """Annotate a single domain"""
        try:
            if domain.domain_type == DomainType.VARIABLE:
                return self._annotate_variable_domain(domain, numbering_scheme)
            elif domain.domain_type == DomainType.CONSTANT:
                return self._annotate_constant_domain(domain)
            elif domain.domain_type == DomainType.LINKER:
                return self._annotate_linker_domain(domain)
            else:
                raise AnnotationError(
                    f"Unknown domain type: {domain.domain_type}",
                    step="domain_type_check",
                )
        except Exception as e:
            raise AnnotationError(
                f"Domain annotation failed: {str(e)}", step="domain_annotation"
            )

    def _get_domain_sequence(self, domain: BiologicDomain) -> str:
        """Get the sequence for a domain from its metadata or parent sequence"""
        # Try to get sequence from metadata first (for test compatibility)
        if "sequence" in domain.metadata:
            return domain.metadata["sequence"]

        # If not in metadata, try to extract from parent sequence
        # This would require the domain to have a reference to its parent sequence
        # For now, we'll raise an error if sequence is not available
        raise AnnotationError(
            f"Domain sequence not available for domain {domain.domain_type}",
            step="sequence_extraction",
        )

    def _annotate_variable_domain(
        self, domain: BiologicDomain, numbering_scheme: NumberingScheme
    ) -> BiologicDomain:
        """Annotate a variable domain using ANARCI"""
        try:
            # Get the sequence for this domain
            domain_sequence = self._get_domain_sequence(domain)

            # Use ANARCI for variable domain annotation
            anarci_result = self._anarci_adapter.annotate_sequence(
                domain_sequence, numbering_scheme
            )

            if not anarci_result.get("success", False):
                raise AnnotationError(
                    "ANARCI annotation failed", step="anarci_annotation"
                )

            # Extract regions from ANARCI result
            regions = self._extract_regions_from_anarci(anarci_result, domain)

            # Extract species and germline information from ANARCI result
            anarci_data = anarci_result.get("data", {})
            species = None
            germline = None
            
            # Extract species from alignment details
            if anarci_data.get("alignment_details"):
                for align_detail in anarci_data["alignment_details"]:
                    if hasattr(align_detail, 'species'):
                        species = align_detail.species
                        break
            
            # Extract germline information from hit table
            if anarci_data.get("hit_table"):
                germline_info = self._extract_germline_from_hit_table(anarci_data["hit_table"])
                germline = germline_info.get("id") if germline_info else None
            
            # Create annotated domain
            annotated_domain = BiologicDomain(
                domain_type=domain.domain_type,
                start_position=domain.start_position,
                end_position=domain.end_position,
                confidence_score=domain.confidence_score,
                metadata={
                    **domain.metadata,
                    "anarci_result": anarci_result.get("data"),
                    "regions": regions,
                    "species": species,
                    "germline": germline,
                },
            )

            return annotated_domain

        except Exception as e:
            raise AnnotationError(
                f"Variable domain annotation failed: {str(e)}",
                step="variable_domain_annotation",
            )

    def _annotate_constant_domain(
        self, domain: BiologicDomain
    ) -> BiologicDomain:
        """Annotate a constant domain using HMMER"""
        try:
            # Get the sequence for this domain
            domain_sequence = self._get_domain_sequence(domain)

            # Use HMMER for isotype detection
            hmmer_result = self._hmmer_adapter.detect_isotype(domain_sequence)

            if not hmmer_result.get("success", False):
                raise AnnotationError(
                    "HMMER isotype detection failed", step="hmmer_detection"
                )

            # Create annotated domain
            annotated_domain = BiologicDomain(
                domain_type=domain.domain_type,
                start_position=domain.start_position,
                end_position=domain.end_position,
                confidence_score=domain.confidence_score,
                metadata={
                    **domain.metadata,
                    "isotype": hmmer_result.get("isotype"),
                    "hmmer_score": hmmer_result.get("score"),
                },
            )

            return annotated_domain

        except Exception as e:
            raise AnnotationError(
                f"Constant domain annotation failed: {str(e)}",
                step="constant_domain_annotation",
            )

    def _annotate_linker_domain(
        self, domain: BiologicDomain
    ) -> BiologicDomain:
        """Annotate a linker domain"""
        try:
            # Linker domains are typically simple and don't require external tools
            # Just mark them as annotated
            annotated_domain = BiologicDomain(
                domain_type=domain.domain_type,
                start_position=domain.start_position,
                end_position=domain.end_position,
                confidence_score=domain.confidence_score,
                metadata={
                    **domain.metadata,
                    "annotated": True,
                    "annotation_method": "linker_domain",
                },
            )

            return annotated_domain

        except Exception as e:
            raise AnnotationError(
                f"Linker domain annotation failed: {str(e)}",
                step="linker_domain_annotation",
            )

    def _extract_regions_from_anarci(
        self, anarci_result: Dict[str, Any], domain: BiologicDomain
    ) -> Dict[str, BiologicFeature]:
        """Extract regions from ANARCI result"""
        regions = {}

        try:
            numbered = anarci_result.get("data", {}).get("numbered", [])
            if numbered:
                # Extract CDR regions
                cdr_regions = self._extract_cdr_regions(numbered, domain)
                regions.update(cdr_regions)

                # Extract FR regions
                fr_regions = self._extract_fr_regions(numbered, domain)
                regions.update(fr_regions)

        except Exception as e:
            logger.warning(f"Error extracting regions from ANARCI: {e}")

        return regions

    def _extract_cdr_regions(
        self, numbered: List, domain: BiologicDomain
    ) -> Dict[str, BiologicFeature]:
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
                    region = BiologicFeature(
                        feature_type=cdr_name,
                        name=cdr_name,
                        value=cdr_sequence,
                        start_position=start,
                        end_position=end,
                        confidence_score=domain.confidence_score,
                        metadata={"source": "ANARCI"},
                    )
                    regions[cdr_name] = region
            except Exception as e:
                logger.warning(
                    f"Could not extract {cdr_name} for domain {domain.domain_type}: {e}"
                )
        return regions

    def _extract_fr_regions(
        self, numbered: List, domain: BiologicDomain
    ) -> Dict[str, BiologicFeature]:
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
                    region = BiologicFeature(
                        feature_type=fr_name,
                        name=fr_name,
                        value=fr_sequence,
                        start_position=start,
                        end_position=end,
                        confidence_score=domain.confidence_score,
                        metadata={"source": "ANARCI"},
                    )
                    regions[fr_name] = region
            except Exception as e:
                logger.warning(
                    f"Could not extract {fr_name} for domain {domain.domain_type}: {e}"
                )
        return regions

    def _extract_region_sequence(
        self, numbered: List, start: int, end: int
    ) -> Optional[str]:
        """Extract sequence for a specific region"""
        try:
            # Extract amino acids from numbered sequence
            region_sequence = ""
            for item in numbered:
                if isinstance(item, dict) and "pos" in item:
                    pos = item["pos"]
                    if start <= pos <= end:
                        aa = item.get("aa", "")
                        region_sequence += aa
            return region_sequence if region_sequence else None
        except Exception as e:
            logger.warning(f"Error extracting region sequence: {e}")
            return None

    def _create_boundary(self, start: int, end: int) -> RegionBoundary:
        """Create a region boundary"""
        return RegionBoundary(start=start, end=end)

    def _calculate_constant_boundary(self, domain: BiologicDomain):
        """Calculate boundary for constant domain"""
        # Implementation would depend on domain sequence analysis
        pass

    def _calculate_linker_boundary(self, domain: BiologicDomain):
        """Calculate boundary for linker domain"""
        # Implementation would depend on domain sequence analysis
        pass

    def _detect_chain_type(self, chain: BiologicChain) -> ChainType:
        """Detect chain type from chain data"""
        try:
            # Try to detect from chain name
            if chain.name:
                return self._detect_chain_type_from_name(chain.name)

            # Try to detect from sequence content
            for sequence in chain.sequences:
                if sequence.sequence_data:
                    # Simple heuristics for chain type detection
                    if "C" in sequence.sequence_data[:10]:  # Constant region
                        return ChainType.HEAVY
                    elif "V" in sequence.sequence_data[:10]:  # Variable region
                        return ChainType.LIGHT

            # Default to HEAVY if we can't determine
            return ChainType.HEAVY

        except Exception as e:
            logger.warning(f"Error detecting chain type: {e}")
            return ChainType.HEAVY

    def _detect_chain_type_from_name(self, chain_name: str) -> ChainType:
        """Detect chain type from chain name"""
        chain_name_lower = chain_name.lower()

        if any(
            keyword in chain_name_lower for keyword in ["heavy", "h", "vh"]
        ):
            return ChainType.HEAVY
        elif any(
            keyword in chain_name_lower
            for keyword in ["light", "l", "vl", "kappa", "lambda"]
        ):
            return ChainType.LIGHT
        elif any(
            keyword in chain_name_lower for keyword in ["scfv", "single"]
        ):
            return ChainType.SCFV
        else:
            # Default to HEAVY if we can't determine
            return ChainType.HEAVY

    def _extract_germline_from_hit_table(self, hit_table: List[List]) -> Dict[str, Any]:
        """Extract germline information from ANARCI hit table"""
        if not hit_table or len(hit_table) < 2:
            return {}

        header = hit_table[0]
        rows = hit_table[1:]

        # Find relevant column indices
        id_idx = header.index("id") if "id" in header else None
        bitscore_idx = header.index("bitscore") if "bitscore" in header else None
        e_value_idx = header.index("evalue") if "evalue" in header else None

        if not rows:
            return {}

        # Get best hit (highest bitscore)
        best_row = max(
            rows,
            key=lambda row: (
                float(row[bitscore_idx]) if bitscore_idx is not None else 0
            ),
        )

        germline_info = {}
        if id_idx is not None:
            germline_info["id"] = best_row[id_idx]
        if bitscore_idx is not None:
            germline_info["bitscore"] = float(best_row[bitscore_idx])
        if e_value_idx is not None:
            germline_info["evalue"] = float(best_row[e_value_idx])

        return germline_info

    def notify_error(self, error: str) -> None:
        """Notify about an error during processing"""
        logger.error(f"Annotation error: {error}")
        self.notify_processing_failed(error)
