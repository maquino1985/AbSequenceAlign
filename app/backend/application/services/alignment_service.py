"""
Alignment service for orchestrating sequence alignment.
Implements the Strategy pattern for different alignment approaches.
"""

from typing import Dict, Any, List

from ...core.base_classes import AbstractProcessingSubject
from ...core.interfaces import ProcessingResult
from ...core.exceptions import AlignmentError, ValidationError
from ...domain.entities import (
    BiologicEntity,
    BiologicSequence,
)
from ...logger import logger


class AlignmentService(AbstractProcessingSubject):
    """Service for orchestrating sequence alignment"""

    def __init__(self) -> None:
        super().__init__()
        self._alignment_strategies = {
            "pairwise": self._pairwise_alignment,
            "multiple": self._multiple_alignment,
            "region_specific": self._region_specific_alignment,
        }

    def align_sequences(
        self,
        sequences: List[BiologicEntity],
        strategy: str = "multiple",
        **kwargs,
    ) -> ProcessingResult:
        """Align multiple antibody sequences"""
        try:
            logger.info(
                f"Starting alignment of {len(sequences)} sequences using {strategy} strategy"
            )
            self.notify_step_completed("start", 0.0)

            # Validate sequences
            if not self._validate_sequences(sequences):
                raise ValidationError(
                    "Invalid sequences for alignment", field="sequences"
                )

            # Select alignment strategy
            if strategy not in self._alignment_strategies:
                raise AlignmentError(
                    f"Unknown alignment strategy: {strategy}",
                    step="strategy_selection",
                )

            alignment_strategy = self._alignment_strategies[strategy]

            # Perform alignment
            self.notify_step_completed("aligning", 0.5)
            alignment_result = alignment_strategy(sequences, **kwargs)

            # Process results
            self.notify_step_completed("processing", 0.8)
            processed_result = self._process_alignment_result(
                alignment_result, sequences
            )

            self.notify_step_completed("complete", 1.0)
            logger.info(f"Alignment completed for {len(sequences)} sequences")

            return ProcessingResult(
                success=True,
                data=processed_result,
                metadata={
                    "strategy": strategy,
                    "sequences_count": len(sequences),
                    "alignment_score": alignment_result.get("score", 0),
                },
            )

        except Exception as e:
            error_msg = f"Alignment failed: {str(e)}"
            logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def align_regions(
        self,
        sequences: List[BiologicEntity],
        region_type: RegionType,
        **kwargs,
    ) -> ProcessingResult:
        """Align specific regions across sequences"""
        try:
            logger.info(f"Starting region alignment for {region_type.value}")
            self.notify_step_completed("start", 0.0)

            # Extract regions from sequences
            regions = self._extract_regions(sequences, region_type)

            if not regions:
                raise AlignmentError(
                    f"No {region_type.value} regions found",
                    step="region_extraction",
                )

            # Align regions
            self.notify_step_completed("aligning", 0.5)
            alignment_result = self._align_region_sequences(regions, **kwargs)

            # Process results
            self.notify_step_completed("processing", 0.8)
            processed_result = self._process_region_alignment_result(
                alignment_result, regions
            )

            self.notify_step_completed("complete", 1.0)
            logger.info(f"Region alignment completed for {region_type.value}")

            return ProcessingResult(
                success=True,
                data=processed_result,
                metadata={
                    "region_type": region_type.value,
                    "regions_count": len(regions),
                    "alignment_score": alignment_result.get("score", 0),
                },
            )

        except Exception as e:
            error_msg = f"Region alignment failed: {str(e)}"
            logger.error(error_msg)
            self.notify_error(error_msg)
            return ProcessingResult(success=False, error=error_msg)

    def _pairwise_alignment(
        self, sequences: List[BiologicEntity], **kwargs
    ) -> Dict[str, Any]:
        """Perform pairwise alignment between sequences"""
        try:
            if len(sequences) != 2:
                raise AlignmentError(
                    "Pairwise alignment requires exactly 2 sequences",
                    step="validation",
                )

            # Extract full sequences
            seq1 = self._extract_full_sequence(sequences[0])
            seq2 = self._extract_full_sequence(sequences[1])

            # Perform pairwise alignment using Biopython
            from Bio import pairwise2

            # Configure alignment parameters
            match_score = kwargs.get("match_score", 2)
            mismatch_score = kwargs.get("mismatch_score", -1)
            gap_open = kwargs.get("gap_open", -10)
            gap_extend = kwargs.get("gap_extend", -0.5)

            # Perform alignment
            alignments = pairwise2.align.globalms(
                seq1, seq2, match_score, mismatch_score, gap_open, gap_extend
            )

            if not alignments:
                raise AlignmentError(
                    "No alignment found", step="pairwise_alignment"
                )

            # Get best alignment
            best_alignment = alignments[0]

            return {
                "type": "pairwise",
                "score": best_alignment.score,
                "aligned_sequences": [
                    best_alignment.seqA,
                    best_alignment.seqB,
                ],
                "start_end": [best_alignment.start, best_alignment.end],
            }

        except Exception as e:
            raise AlignmentError(
                f"Pairwise alignment failed: {str(e)}",
                step="pairwise_alignment",
            )

    def _multiple_alignment(
        self, sequences: List[BiologicEntity], **kwargs
    ) -> Dict[str, Any]:
        """Perform multiple sequence alignment"""
        try:
            # Extract full sequences
            seqs = [self._extract_full_sequence(seq) for seq in sequences]

            # Use MUSCLE for multiple alignment
            alignment_result = self._run_muscle_alignment(seqs, **kwargs)

            return {
                "type": "multiple",
                "score": alignment_result.get("score", 0),
                "aligned_sequences": alignment_result.get(
                    "aligned_sequences", []
                ),
                "consensus": alignment_result.get("consensus", ""),
                "length": alignment_result.get("length", 0),
            }

        except Exception as e:
            raise AlignmentError(
                f"Multiple alignment failed: {str(e)}",
                step="multiple_alignment",
            )

    def _region_specific_alignment(
        self, sequences: List[BiologicEntity], **kwargs
    ) -> Dict[str, Any]:
        """Perform region-specific alignment"""
        try:
            region_type = kwargs.get("region_type", RegionType.CDR3)

            # Extract specific regions
            regions = self._extract_regions(sequences, region_type)

            if not regions:
                raise AlignmentError(
                    f"No {region_type.value} regions found",
                    step="region_extraction",
                )

            # Align regions
            alignment_result = self._align_region_sequences(regions, **kwargs)

            return {
                "type": "region_specific",
                "region_type": region_type.value,
                "score": alignment_result.get("score", 0),
                "aligned_sequences": alignment_result.get(
                    "aligned_sequences", []
                ),
                "region_info": alignment_result.get("region_info", {}),
            }

        except Exception as e:
            raise AlignmentError(
                f"Region-specific alignment failed: {str(e)}",
                step="region_alignment",
            )

    def _run_muscle_alignment(
        self, sequences: List[str], **kwargs
    ) -> Dict[str, Any]:
        """Run MUSCLE alignment"""
        try:
            # For now, use a simplified approach
            # In a real implementation, this would call the MUSCLE adapter

            # Simple multiple alignment (placeholder)
            max_length = max(len(seq) for seq in sequences)
            aligned_sequences = []

            for seq in sequences:
                # Pad sequences to same length
                padded_seq = seq + "-" * (max_length - len(seq))
                aligned_sequences.append(padded_seq)

            # Calculate simple consensus
            consensus = self._calculate_consensus(aligned_sequences)

            return {
                "aligned_sequences": aligned_sequences,
                "consensus": consensus,
                "length": max_length,
                "score": self._calculate_alignment_score(aligned_sequences),
            }

        except Exception as e:
            raise AlignmentError(
                f"MUSCLE alignment failed: {str(e)}", step="muscle_alignment"
            )

    def _align_region_sequences(
        self, regions: List[Dict[str, Any]], **kwargs
    ) -> Dict[str, Any]:
        """Align region sequences"""
        try:
            # Extract region sequences
            region_sequences = [region["sequence"] for region in regions]

            # Perform multiple alignment on regions
            alignment_result = self._run_muscle_alignment(
                region_sequences, **kwargs
            )

            # Add region information
            alignment_result["region_info"] = {
                "names": [region["name"] for region in regions],
                "types": [region["type"] for region in regions],
                "positions": [region["position"] for region in regions],
            }

            return alignment_result

        except Exception as e:
            raise AlignmentError(
                f"Region sequence alignment failed: {str(e)}",
                step="region_sequence_alignment",
            )

    def _extract_regions(
        self, sequences: List[BiologicEntity], region_type: RegionType
    ) -> List[Dict[str, Any]]:
        """Extract specific regions from sequences"""
        regions = []

        for i, sequence in enumerate(sequences):
            for chain in sequence.chains:
                for biologic_sequence in chain.sequences:
                    for domain in biologic_sequence.domains:
                        if domain.domain_type.upper() == "VARIABLE":
                            # Extract features that match the region type
                            for feature in domain.features:
                                if (
                                    feature.feature_type.upper()
                                    == region_type.value.upper()
                                ):
                                    regions.append(
                                        {
                                            "name": f"{sequence.name}_{chain.name}_{feature.name}",
                                            "sequence": feature.value,
                                            "type": feature.feature_type,
                                            "position": (
                                                feature.start_position,
                                                feature.end_position,
                                            ),
                                            "source": {
                                                "sequence": sequence.name,
                                                "chain": chain.name,
                                                "domain": domain.domain_type,
                                            },
                                        }
                                    )

        return regions

    def _extract_full_sequence(self, sequence: BiologicEntity) -> str:
        """Extract full sequence from biologic entity"""
        full_sequence = ""

        for chain in sequence.chains:
            for biologic_sequence in chain.sequences:
                full_sequence += biologic_sequence.sequence_data

        return full_sequence

    def _calculate_consensus(self, aligned_sequences: List[str]) -> str:
        """Calculate consensus sequence from aligned sequences"""
        if not aligned_sequences:
            return ""

        consensus = ""
        length = len(aligned_sequences[0])

        for pos in range(length):
            # Count amino acids at this position
            amino_acids = [
                seq[pos] for seq in aligned_sequences if pos < len(seq)
            ]
            amino_acids = [aa for aa in amino_acids if aa != "-"]

            if not amino_acids:
                consensus += "-"
                continue

            # Find most common amino acid
            from collections import Counter

            aa_counts = Counter(amino_acids)
            most_common = aa_counts.most_common(1)[0][0]
            consensus += most_common

        return consensus

    def _calculate_alignment_score(
        self, aligned_sequences: List[str]
    ) -> float:
        """Calculate alignment score"""
        if not aligned_sequences or len(aligned_sequences) < 2:
            return 0.0

        total_score = 0.0
        length = len(aligned_sequences[0])

        for pos in range(length):
            # Get amino acids at this position
            amino_acids = [
                seq[pos] for seq in aligned_sequences if pos < len(seq)
            ]
            amino_acids = [aa for aa in amino_acids if aa != "-"]

            if len(amino_acids) < 2:
                continue

            # Calculate conservation score
            unique_aas = set(amino_acids)
            if len(unique_aas) == 1:
                total_score += 1.0  # Perfect conservation
            else:
                total_score += 1.0 / len(unique_aas)  # Partial conservation

        return total_score / length if length > 0 else 0.0

    def _process_alignment_result(
        self,
        alignment_result: Dict[str, Any],
        sequences: List[BiologicEntity],
    ) -> Dict[str, Any]:
        """Process alignment result"""
        return {
            "alignment": alignment_result,
            "sequences": [seq.name for seq in sequences],
            "statistics": {
                "length": alignment_result.get("length", 0),
                "score": alignment_result.get("score", 0),
                "type": alignment_result.get("type", "unknown"),
            },
        }

    def _process_region_alignment_result(
        self, alignment_result: Dict[str, Any], regions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process region alignment result"""
        return {
            "alignment": alignment_result,
            "regions": [region["name"] for region in regions],
            "statistics": {
                "length": alignment_result.get("length", 0),
                "score": alignment_result.get("score", 0),
                "type": "region_specific",
                "region_info": alignment_result.get("region_info", {}),
            },
        }

    def _validate_sequences(self, sequences: List[BiologicEntity]) -> bool:
        """Validate sequences for alignment"""
        if not sequences or len(sequences) < 2:
            return False

        for sequence in sequences:
            if not sequence or not sequence.chains:
                return False

        return True
