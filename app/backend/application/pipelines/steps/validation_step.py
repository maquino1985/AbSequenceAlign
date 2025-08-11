"""
Validation pipeline step for validating sequences before processing.
Implements the AbstractPipelineStep interface.
"""

from typing import Any, List, Dict
import logging

from backend.core.base_classes import AbstractPipelineStep
from backend.core.interfaces import PipelineContext
from backend.core.exceptions import ValidationError
from backend.domain.models import SequenceValidator


class SequenceValidationStep(AbstractPipelineStep):
    """Pipeline step for validating sequences"""

    def __init__(self, min_length: int = 1, max_length: int = 10000):
        super().__init__("sequence_validation")
        self.min_length = min_length
        self.max_length = max_length
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def _execute_step(self, context: PipelineContext) -> Dict[str, Any]:
        """Execute the validation step"""
        sequence = context.sequence

        # Validate sequence
        validation_result = self._validate_sequence(sequence)

        if not validation_result["is_valid"]:
            context.errors.extend(validation_result["errors"])
            raise ValidationError(
                f"Sequence validation failed: {', '.join(validation_result['errors'])}",
                field="sequence",
                value=(
                    sequence.sequence
                    if hasattr(sequence, "sequence")
                    else str(sequence)
                ),
            )

        self._logger.info(f"Sequence validation passed for: {sequence.name}")

        return {
            "is_valid": True,
            "sequence_length": (
                len(sequence.sequence) if hasattr(sequence, "sequence") else 0
            ),
            "sequence_name": (
                sequence.name if hasattr(sequence, "name") else "unknown"
            ),
        }

    def _validate_sequence(self, sequence: Any) -> Dict[str, Any]:
        """Validate a sequence"""
        errors = []

        # Check if sequence has required attributes
        if not hasattr(sequence, "sequence"):
            errors.append("Sequence object must have a 'sequence' attribute")
            return {"is_valid": False, "errors": errors}

        if not hasattr(sequence, "name"):
            errors.append("Sequence object must have a 'name' attribute")
            return {"is_valid": False, "errors": errors}

        sequence_str = sequence.sequence
        sequence_name = sequence.name

        # Validate sequence string
        if not sequence_str or not isinstance(sequence_str, str):
            errors.append("Sequence must be a non-empty string")
            return {"is_valid": False, "errors": errors}

        # Validate sequence length
        if not SequenceValidator.validate_sequence_length(
            sequence_str, self.min_length, self.max_length
        ):
            errors.append(
                f"Sequence length must be between {self.min_length} and "
                f"{self.max_length} characters, got {len(sequence_str)}"
            )

        # Validate amino acid sequence
        if not SequenceValidator.validate_amino_acid_sequence(sequence_str):
            errors.append("Sequence contains invalid amino acid characters")

        # Validate sequence name
        if not sequence_name or not isinstance(sequence_name, str):
            errors.append("Sequence name must be a non-empty string")

        return {"is_valid": len(errors) == 0, "errors": errors}

    def can_execute(self, context: PipelineContext) -> bool:
        """Check if this step can execute given the current context"""
        return hasattr(context.sequence, "sequence") and hasattr(
            context.sequence, "name"
        )


class AntibodySequenceValidationStep(SequenceValidationStep):
    """Pipeline step for validating antibody sequences specifically"""

    def __init__(self, min_length: int = 50, max_length: int = 10000):
        super().__init__(min_length, max_length)
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def _execute_step(self, context: PipelineContext) -> Dict[str, Any]:
        """Execute the antibody sequence validation step"""
        # First do basic validation
        basic_result = super()._execute_step(context)

        # Then do antibody-specific validation
        antibody_result = self._validate_antibody_sequence(context.sequence)

        if not antibody_result["is_valid"]:
            context.errors.extend(antibody_result["errors"])
            raise ValidationError(
                f"Antibody sequence validation failed: "
                f"{', '.join(antibody_result['errors'])}",
                field="sequence",
                value=context.sequence.sequence,
            )

        # Combine results
        result = basic_result.copy()
        result.update(antibody_result)

        self._logger.info(
            f"Antibody sequence validation passed for: {context.sequence.name}"
        )

        return result

    def _validate_antibody_sequence(self, sequence: Any) -> Dict[str, Any]:
        """Validate antibody-specific sequence properties"""
        errors = []
        warnings = []

        sequence_str = sequence.sequence.upper()

        # Check for common antibody patterns
        if not self._has_antibody_patterns(sequence_str):
            warnings.append(
                "Sequence does not contain typical antibody patterns"
            )

        # Check for CDR-like regions (simplified check)
        if not self._has_cdr_like_regions(sequence_str):
            warnings.append("Sequence does not contain CDR-like regions")

        # Check for constant region patterns
        if not self._has_constant_region_patterns(sequence_str):
            warnings.append(
                "Sequence does not contain constant region patterns"
            )

        # Check for proper cysteine patterns
        if not self._has_proper_cysteine_patterns(sequence_str):
            errors.append(
                "Sequence does not have proper cysteine patterns for antibody structure"
            )

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def _has_antibody_patterns(self, sequence: str) -> bool:
        """Check if sequence has common antibody patterns"""
        # Check for common antibody motifs
        antibody_motifs = [
            "CXXXC",  # Disulfide bond pattern
            "WGXG",  # CDR pattern
            "YXC",  # Framework pattern
        ]

        for motif in antibody_motifs:
            if motif in sequence:
                return True

        return False

    def _has_cdr_like_regions(self, sequence: str) -> bool:
        """Check if sequence has CDR-like regions"""
        # Simplified check for CDR-like regions
        # CDRs typically have higher variability and specific patterns

        # Check for regions with high variability (simplified)
        if len(sequence) < 100:
            return False

        # Look for regions with high glycine content (common in CDRs)
        glycine_count = sequence.count("G")
        if glycine_count / len(sequence) > 0.15:  # More than 15% glycine
            return True

        return False

    def _has_constant_region_patterns(self, sequence: str) -> bool:
        """Check if sequence has constant region patterns"""
        # Check for constant region motifs
        constant_motifs = [
            "EPKSC",  # IgG constant region
            "VVSVL",  # IgG constant region
            "TVLHQ",  # IgG constant region
        ]

        for motif in constant_motifs:
            if motif in sequence:
                return True

        return False

    def _has_proper_cysteine_patterns(self, sequence: str) -> bool:
        """Check if sequence has proper cysteine patterns for antibody structure"""
        # Antibodies typically have even number of cysteines for disulfide bonds
        cysteine_count = sequence.count("C")

        if cysteine_count == 0:
            return False  # No cysteines for disulfide bonds

        if cysteine_count % 2 != 0:
            return False  # Odd number of cysteines

        # Check for proper spacing (simplified)
        if len(sequence) > 200 and cysteine_count < 4:
            return False  # Long sequence should have more cysteines

        return True


class ChainValidationStep(AbstractPipelineStep):
    """Pipeline step for validating antibody chains"""

    def __init__(self):
        super().__init__("chain_validation")
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def _execute_step(self, context: PipelineContext) -> Dict[str, Any]:
        """Execute the chain validation step"""
        sequence = context.sequence

        # Validate chain structure
        validation_result = self._validate_chain_structure(sequence)

        if not validation_result["is_valid"]:
            context.errors.extend(validation_result["errors"])
            raise ValidationError(
                f"Chain validation failed: {', '.join(validation_result['errors'])}",
                field="chain",
                value=str(sequence),
            )

        self._logger.info(f"Chain validation passed for: {sequence.name}")

        return validation_result

    def _validate_chain_structure(self, sequence: Any) -> Dict[str, Any]:
        """Validate chain structure"""
        errors = []

        # Check if sequence has chains
        if not hasattr(sequence, "chains"):
            errors.append("Sequence must have a 'chains' attribute")
            return {"is_valid": False, "errors": errors}

        chains = sequence.chains

        if not chains:
            errors.append("Sequence must have at least one chain")
            return {"is_valid": False, "errors": errors}

        # Validate each chain
        for i, chain in enumerate(chains):
            chain_errors = self._validate_individual_chain(chain, i)
            errors.extend(chain_errors)

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "chain_count": len(chains),
        }

    def _validate_individual_chain(self, chain: Any, index: int) -> List[str]:
        """Validate an individual chain"""
        errors = []

        # Check required attributes
        required_attrs = ["name", "chain_type", "sequence", "domains"]
        for attr in required_attrs:
            if not hasattr(chain, attr):
                errors.append(f"Chain {index} must have '{attr}' attribute")

        if errors:
            return errors

        # Validate chain type
        if not hasattr(chain.chain_type, "value"):
            errors.append(f"Chain {index} must have a valid chain type")

        # Validate sequence
        if not chain.sequence or not isinstance(chain.sequence, str):
            errors.append(f"Chain {index} must have a valid sequence")

        # Validate domains
        if not isinstance(chain.domains, list):
            errors.append(f"Chain {index} must have a list of domains")

        return errors

    def can_execute(self, context: PipelineContext) -> bool:
        """Check if this step can execute given the current context"""
        return hasattr(context.sequence, "chains")
