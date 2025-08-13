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
    FeatureType,
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

from backend.annotation.anarci_result_processor import AnarciResultProcessor


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
        # logger.info(f"Starting annotation for sequence: {sequence.name}")

        try:
            processor = AnarciResultProcessor(
                sequence, numbering_scheme=numbering_scheme.value
            )
            print(processor.results)
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

            # Process sequences and detect/create domains
            annotated_sequences = []
            for sequence in chain.sequences:
                # Detect and create domains from sequence data
                detected_domains = self._detect_domains_from_sequence(
                    sequence, numbering_scheme
                )

                # Annotate each detected domain
                annotated_domains = []
                for domain in detected_domains:
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
            # Check if ANARCI result is already in metadata (from domain detection)
            if "anarci_result" in domain.metadata:
                anarci_result = {
                    "success": True,
                    "data": domain.metadata["anarci_result"],
                }
            else:
                # Get the sequence for this domain
                domain_sequence = self._get_domain_sequence(domain)

                # Use ANARCI for variable domain annotation
                anarci_result = self._anarci_adapter.number_sequence(
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
            species = domain.metadata.get("species")
            germline = domain.metadata.get("germline")

            # If not already extracted, try to extract from ANARCI result
            if not species:
                if anarci_data.get("alignment_details"):
                    for align_detail in anarci_data["alignment_details"]:
                        if hasattr(align_detail, "species"):
                            species = align_detail.species
                            break

            if not germline:
                if anarci_data.get("hit_table"):
                    germline_info = self._extract_germline_from_hit_table(
                        anarci_data["hit_table"]
                    )
                    germline = (
                        germline_info.get("id") if germline_info else None
                    )

            # Create annotated domain with features
            annotated_domain = BiologicDomain(
                domain_type=domain.domain_type,
                start_position=domain.start_position,
                end_position=domain.end_position,
                confidence_score=domain.confidence_score,
                features=list(regions.values()),  # Add features to the domain
                metadata={
                    **domain.metadata,
                    "anarci_result": anarci_data,
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
            # Check if HMMER result is already in metadata (from domain detection)
            if "hmmer_result" in domain.metadata:
                hmmer_result = domain.metadata["hmmer_result"]
            else:
                # Get the sequence for this domain
                domain_sequence = self._get_domain_sequence(domain)

                # Use HMMER for isotype detection
                hmmer_result = self._hmmer_adapter.detect_isotype(
                    domain_sequence
                )

                if not hmmer_result.get("success", False):
                    raise AnnotationError(
                        "HMMER isotype detection failed",
                        step="hmmer_detection",
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
            data = anarci_result.get("data", {})
            # The results are nested under data.data.results
            nested_data = data.get("data", {})
            results = nested_data.get("results", [])
            if results:
                for result in results:
                    numbered_list = result.get("numbered", [])

                    # Each item in numbered_list is (numbered_data, start, end)
                    for numbered_item in numbered_list:
                        if (
                            isinstance(numbered_item, tuple)
                            and len(numbered_item) == 3
                        ):
                            numbered_data, start, end = numbered_item
                            if numbered_data:
                                # Extract CDR regions from this numbered data
                                cdr_regions = self._extract_cdr_regions(
                                    numbered_data, domain
                                )
                                regions.update(cdr_regions)

                                # Extract FR regions from this numbered data
                                fr_regions = self._extract_fr_regions(
                                    numbered_data, domain
                                )
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
                        feature_type=FeatureType(cdr_name),
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
                        feature_type=FeatureType(fr_name),
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

            # Handle ANARCI format: [((pos, chain), aa), ...]
            for item in numbered:
                if isinstance(item, tuple) and len(item) == 2:
                    pos_tuple, aa = item
                    if isinstance(pos_tuple, tuple) and len(pos_tuple) == 2:
                        pos, chain = pos_tuple
                        if isinstance(pos, int) and start <= pos <= end:
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

    def _detect_domains_from_sequence(
        self, sequence: BiologicSequence, numbering_scheme: NumberingScheme
    ) -> List[BiologicDomain]:
        """Detect domains from sequence data using ANARCI and HMMER"""
        try:
            logger.debug(
                f"Detecting domains from sequence: {sequence.sequence_data[:50]}..."
            )

            domains = []
            sequence_data = sequence.sequence_data

            # Determine antibody type and domain structure
            antibody_type = self._detect_antibody_type(sequence_data)
            logger.debug(f"Detected antibody type: {antibody_type}")

            if antibody_type == "scfv":
                # scFv: 2 variable domains (VH + VL) + linker (no constant domain)
                domains = self._detect_scfv_domains(
                    sequence_data, numbering_scheme
                )
            elif antibody_type == "dvd_ig":
                # DvD-Ig: 2 variable domains + 1 constant domain
                domains = self._detect_dvd_ig_domains(
                    sequence_data, numbering_scheme
                )
            else:
                # IgG: 1 variable domain + 1 constant domain
                domains = self._detect_igg_domains(
                    sequence_data, numbering_scheme
                )

            # If no domains detected, create a single domain with the full sequence
            if not domains:
                logger.warning(
                    f"No domains detected for sequence, creating default domain"
                )
                default_domain = BiologicDomain(
                    domain_type=DomainType.VARIABLE,
                    start_position=1,
                    end_position=len(sequence_data),
                    confidence_score=0.5,
                    metadata={
                        "sequence": sequence_data,
                        "note": "Default domain - no specific detection",
                    },
                )
                domains.append(default_domain)

            logger.debug(f"Detected {len(domains)} domains for sequence")
            return domains

        except Exception as e:
            logger.error(f"Error detecting domains from sequence: {e}")
            # Return a default domain if detection fails
            return [
                BiologicDomain(
                    domain_type=DomainType.VARIABLE,
                    start_position=1,
                    end_position=len(sequence.sequence_data),
                    confidence_score=0.0,
                    metadata={
                        "sequence": sequence.sequence_data,
                        "error": str(e),
                    },
                )
            ]

    def _detect_antibody_type(self, sequence: str) -> str:
        """Detect antibody type based on sequence characteristics"""
        sequence_upper = sequence.upper()

        # Check for scFv linker patterns
        if (
            "GGGGSGGGGSGGGGSGGGGS" in sequence_upper
            or "GGGGSGGGGS" in sequence_upper
        ):
            return "scfv"

        # Check for DvD-Ig patterns (two variable domains)
        # Look for two consecutive variable domain patterns
        variable_patterns = [
            "WGQGTLVTVSS",
            "FGQGTKVEIK",
            "WGQGTQVTVSS",
            "FGQGTKLEIK",
        ]
        pattern_count = 0
        for pattern in variable_patterns:
            if pattern in sequence_upper:
                pattern_count += 1

        if pattern_count >= 2:
            return "dvd_ig"

        # Default to IgG
        return "igg"

    def _detect_scfv_domains(
        self, sequence: str, numbering_scheme: NumberingScheme
    ) -> List[BiologicDomain]:
        """Detect domains for scFv: 2 variable domains + linker"""
        domains = []

        # Split scFv into VH and VL domains
        vh_end, vl_start = self._detect_scfv_domain_boundaries(sequence)

        if vh_end > 0:
            # VH domain
            vh_sequence = sequence[:vh_end]
            vh_domain = self._create_variable_domain(
                vh_sequence, 1, vh_end, numbering_scheme, "VH"
            )
            domains.append(vh_domain)

        if vl_start > 0 and vl_start < len(sequence):
            # VL domain
            vl_sequence = sequence[
                vl_start - 1 :
            ]  # -1 because positions are 1-indexed
            vl_domain = self._create_variable_domain(
                vl_sequence, vl_start, len(sequence), numbering_scheme, "VL"
            )
            domains.append(vl_domain)

        return domains

    def _detect_dvd_ig_domains(
        self, sequence: str, numbering_scheme: NumberingScheme
    ) -> List[BiologicDomain]:
        """Detect domains for DvD-Ig: 2 variable domains + 1 constant domain"""
        domains = []

        # Detect domain boundaries
        v1_end, v2_start = self._detect_dvd_ig_variable_boundaries(sequence)
        c_start = self._detect_constant_domain_start(sequence, v2_start)

        # First variable domain
        if v1_end > 0:
            v1_sequence = sequence[:v1_end]
            v1_domain = self._create_variable_domain(
                v1_sequence, 1, v1_end, numbering_scheme, "V1"
            )
            domains.append(v1_domain)

        # Second variable domain
        if v2_start > 0 and v2_start < len(sequence):
            v2_end = c_start if c_start > v2_start else len(sequence)
            v2_sequence = sequence[
                v2_start - 1 : v2_end
            ]  # -1 because positions are 1-indexed
            v2_domain = self._create_variable_domain(
                v2_sequence, v2_start, v2_end, numbering_scheme, "V2"
            )
            domains.append(v2_domain)

        # Constant domain
        if c_start > 0 and c_start < len(sequence):
            c_sequence = sequence[
                c_start - 1 :
            ]  # -1 because positions are 1-indexed
            c_domain = self._create_constant_domain(
                c_sequence, c_start, len(sequence)
            )
            domains.append(c_domain)

        return domains

    def _detect_igg_domains(
        self, sequence: str, numbering_scheme: NumberingScheme
    ) -> List[BiologicDomain]:
        """Detect domains for IgG: 1 variable domain + 1 constant domain"""
        domains = []

        # Detect domain boundaries
        v_end, c_start = self._detect_igg_domain_boundaries(sequence)

        # Variable domain
        if v_end > 0:
            v_sequence = sequence[:v_end]
            v_domain = self._create_variable_domain(
                v_sequence, 1, v_end, numbering_scheme, "V"
            )
            domains.append(v_domain)

        # Constant domain
        if c_start > 0 and c_start < len(sequence):
            c_sequence = sequence[
                c_start - 1 :
            ]  # -1 because positions are 1-indexed
            c_domain = self._create_constant_domain(
                c_sequence, c_start, len(sequence)
            )
            domains.append(c_domain)

        return domains

    def _create_variable_domain(
        self,
        sequence: str,
        start: int,
        end: int,
        numbering_scheme: NumberingScheme,
        domain_name: str,
    ) -> BiologicDomain:
        """Create a variable domain with ANARCI annotation"""
        try:
            anarci_result = self._anarci_adapter.number_sequence(
                sequence, numbering_scheme
            )

            metadata = {
                "sequence": sequence,
                "domain_name": domain_name,
                "numbering_scheme": numbering_scheme.value,
            }

            if anarci_result.get("success", False):
                metadata["anarci_result"] = anarci_result
                # Extract species and germline info
                numbered = anarci_result.get("data", {}).get("results", [])
                for result in numbered:
                    alignment_details = result.get("alignment_details", [])
                    for alignment in alignment_details:
                        if alignment.get("species"):
                            metadata["species"] = alignment["species"]
                        if alignment.get("germlines"):
                            germlines = alignment["germlines"]
                            v_gene = germlines.get("v_gene", [None, 0])[0]
                            j_gene = germlines.get("j_gene", [None, 0])[0]
                            if v_gene and j_gene:
                                metadata["germline"] = (
                                    f"{v_gene[1]}/{j_gene[1]}"
                                )
                            elif v_gene:
                                metadata["germline"] = v_gene[1]
                            elif j_gene:
                                metadata["germline"] = j_gene[1]
                            break
                    if "species" in metadata:
                        break

            return BiologicDomain(
                domain_type=DomainType.VARIABLE,
                start_position=start,
                end_position=end,
                confidence_score=1.0,
                metadata=metadata,
            )
        except Exception as e:
            logger.warning(
                f"Error creating variable domain {domain_name}: {e}"
            )
            return BiologicDomain(
                domain_type=DomainType.VARIABLE,
                start_position=start,
                end_position=end,
                confidence_score=0.8,
                metadata={
                    "sequence": sequence,
                    "domain_name": domain_name,
                    "error": str(e),
                },
            )

    def _create_constant_domain(
        self, sequence: str, start: int, end: int
    ) -> BiologicDomain:
        """Create a constant domain with HMMER isotype detection"""
        try:
            hmmer_result = self._hmmer_adapter.detect_isotype(sequence)

            metadata = {
                "sequence": sequence,
                "isotype": (
                    hmmer_result.get("isotype")
                    if hmmer_result.get("success", False)
                    else None
                ),
                "hmmer_score": (
                    hmmer_result.get("score")
                    if hmmer_result.get("success", False)
                    else None
                ),
            }

            if hmmer_result.get("success", False):
                metadata["hmmer_result"] = hmmer_result

            return BiologicDomain(
                domain_type=DomainType.CONSTANT,
                start_position=start,
                end_position=end,
                confidence_score=(
                    1.0 if hmmer_result.get("success", False) else 0.8
                ),
                metadata=metadata,
            )
        except Exception as e:
            logger.warning(f"Error creating constant domain: {e}")
            return BiologicDomain(
                domain_type=DomainType.CONSTANT,
                start_position=start,
                end_position=end,
                confidence_score=0.7,
                metadata={"sequence": sequence, "error": str(e)},
            )

    def _detect_chain_type_from_name(self, chain_name: str) -> ChainType:
        """Detect chain type from chain name"""
        chain_name_lower = chain_name.lower()

        if any(
            keyword in chain_name_lower for keyword in ["heavy", "h", "vh"]
        ):
            return ChainType.HEAVY
        elif any(
            keyword in chain_name_lower
            for keyword in ["light", "l", "vl", "kappa", "lambda", "k", "l"]
        ):
            return ChainType.LIGHT
        elif any(
            keyword in chain_name_lower for keyword in ["scfv", "single"]
        ):
            return ChainType.SCFV
        else:
            # Default to HEAVY if we can't determine
            return ChainType.HEAVY

    def _extract_germline_from_hit_table(
        self, hit_table: List[List]
    ) -> Dict[str, Any]:
        """Extract germline information from ANARCI hit table"""
        if not hit_table or len(hit_table) < 2:
            return {}

        header = hit_table[0]
        rows = hit_table[1:]

        # Find relevant column indices
        id_idx = header.index("id") if "id" in header else None
        bitscore_idx = (
            header.index("bitscore") if "bitscore" in header else None
        )
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

    def _detect_scfv_domain_boundaries(self, sequence: str) -> tuple[int, int]:
        """Detect VH and VL domain boundaries in scFv sequence"""
        sequence_upper = sequence.upper()

        # Look for linker patterns to separate VH and VL
        linker_patterns = [
            "GGGGSGGGGSGGGGSGGGGS",  # Long linker
            "GGGGSGGGGSGGGGS",  # Medium linker
            "GGGGSGGGGS",  # Short linker
        ]

        for pattern in linker_patterns:
            pos = sequence_upper.find(pattern)
            if pos != -1:
                vh_end = pos
                vl_start = (
                    pos + len(pattern) + 1
                )  # +1 because positions are 1-indexed
                logger.debug(
                    f"Found scFv linker pattern, VH ends at {vh_end}, VL starts at {vl_start}"
                )
                return vh_end, vl_start

        # Fallback: use heuristics
        if len(sequence) > 200:
            vh_end = min(120, len(sequence) // 2)
            vl_start = vh_end + 1
            logger.debug(
                f"Using heuristic for scFv: VH ends at {vh_end}, VL starts at {vl_start}"
            )
            return vh_end, vl_start

        return 0, 0

    def _detect_dvd_ig_variable_boundaries(
        self, sequence: str
    ) -> tuple[int, int]:
        """Detect boundaries between two variable domains in DvD-Ig"""
        sequence_upper = sequence.upper()

        # Look for variable domain ending patterns
        variable_end_patterns = [
            "WGQGTLVTVSS",  # Heavy chain ending
            "FGQGTKVEIK",  # Light chain ending
            "WGQGTQVTVSS",  # Alternative ending
            "FGQGTKLEIK",  # Alternative ending
        ]

        v1_end = 0
        v2_start = 0

        # Find first variable domain end
        for pattern in variable_end_patterns:
            pos = sequence_upper.find(pattern)
            if pos != -1:
                v1_end = pos + len(pattern)
                break

        # Find second variable domain start (after first variable domain)
        if v1_end > 0:
            remaining_sequence = sequence_upper[v1_end:]
            for pattern in variable_end_patterns:
                pos = remaining_sequence.find(pattern)
                if pos != -1:
                    v2_start = (
                        v1_end + pos + len(pattern) + 1
                    )  # +1 because positions are 1-indexed
                    break

        return v1_end, v2_start

    def _detect_igg_domain_boundaries(self, sequence: str) -> tuple[int, int]:
        """Detect variable and constant domain boundaries in IgG"""
        sequence_upper = sequence.upper()

        # Look for variable domain ending patterns
        variable_end_patterns = [
            "WGQGTLVTVSS",  # Heavy chain ending
            "FGQGTKVEIK",  # Light chain ending
            "WGQGTQVTVSS",  # Alternative ending
            "FGQGTKLEIK",  # Alternative ending
        ]

        v_end = 0
        c_start = 0

        for pattern in variable_end_patterns:
            pos = sequence_upper.find(pattern)
            if pos != -1:
                v_end = pos + len(pattern)
                c_start = v_end + 1  # Next position after variable domain
                logger.debug(
                    f"Found IgG variable domain ending pattern '{pattern}' at position {v_end}"
                )
                break

        # If no pattern found, use heuristics
        if v_end == 0:
            if len(sequence) > 200:
                v_end = min(128, len(sequence) // 2)
                c_start = v_end + 1
                logger.debug(
                    f"Using heuristic for IgG: variable domain ends at position {v_end}"
                )
            else:
                v_end = len(sequence)
                c_start = 0
                logger.debug(
                    f"Short IgG sequence, treating as variable domain only"
                )

        return v_end, c_start

    def _detect_constant_domain_start(
        self, sequence: str, after_position: int
    ) -> int:
        """Find the start of constant domain after a given position"""
        if after_position >= len(sequence):
            return 0

        remaining_sequence = sequence[after_position:]

        # Look for constant domain start patterns
        constant_start_patterns = [
            "QVQLKQS",  # Heavy chain constant start
            "DIVMTQS",  # Light chain constant start
            "QVQLVES",  # Alternative heavy start
        ]

        for pattern in constant_start_patterns:
            pos = remaining_sequence.find(pattern)
            if pos != -1:
                return (
                    after_position + pos + 1
                )  # +1 because positions are 1-indexed

        # If no pattern found, look for the first occurrence of typical constant domain amino acids
        for i, char in enumerate(remaining_sequence):
            if char in "QVDE" and i > 10:  # Skip potential linker regions
                return (
                    after_position + i + 1
                )  # +1 because positions are 1-indexed

        # Fallback: start after the given position
        return after_position + 1
