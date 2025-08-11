"""
Shared validation utilities for the AbSequenceAlign backend.
Consolidates duplicate validation functions across the codebase.
"""

from typing import List, Dict, Any, Optional
from backend.domain.entities import BiologicEntity, BiologicChain
from backend.logger import logger


class ValidationUtils:
    """Shared validation utilities for biologic entities and sequences"""

    @staticmethod
    def validate_sequence(sequence: BiologicEntity) -> bool:
        """
        Validate a biologic sequence entity.

        Args:
            sequence: The biologic entity to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Basic validation - sequence should have a name and at least one chain
            if not sequence.name or not sequence.chains:
                logger.warning(f"Invalid sequence: missing name or chains")
                return False

            # Each chain should have at least one sequence with domains
            for chain in sequence.chains:
                if not chain.sequences:
                    logger.warning(
                        f"Invalid chain {chain.name}: missing sequences"
                    )
                    return False
                
                # Check that at least one sequence has domains
                has_domains = False
                for sequence in chain.sequences:
                    if sequence.domains:
                        has_domains = True
                        break
                
                if not has_domains:
                    logger.warning(
                        f"Invalid chain {chain.name}: no sequences have domains"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Sequence validation failed: {str(e)}")
            return False

    @staticmethod
    def validate_sequences(sequences: List[BiologicEntity]) -> bool:
        """
        Validate a list of biologic sequences.

        Args:
            sequences: List of biologic entities to validate

        Returns:
            bool: True if all valid, False otherwise
        """
        if not sequences:
            logger.warning("Empty sequences list")
            return False

        for sequence in sequences:
            if not ValidationUtils.validate_sequence(sequence):
                return False

        return True

    @staticmethod
    def validate_chain(chain: BiologicChain) -> bool:
        """
        Validate a biologic chain.

        Args:
            chain: The biologic chain to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not chain.name or not chain.sequences:
                logger.warning(f"Invalid chain: missing name or sequences")
                return False

            return True

        except Exception as e:
            logger.error(f"Chain validation failed: {str(e)}")
            return False

    @staticmethod
    def validate_amino_acid_sequence(sequence: str) -> bool:
        """
        Validate an amino acid sequence string.

        Args:
            sequence: The amino acid sequence to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not sequence or not isinstance(sequence, str):
            return False

        # Standard amino acid alphabet
        valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
        sequence_upper = sequence.upper()

        return all(aa in valid_amino_acids for aa in sequence_upper)

    @staticmethod
    def validate_nucleotide_sequence(sequence: str) -> bool:
        """
        Validate a nucleotide sequence string.

        Args:
            sequence: The nucleotide sequence to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not sequence or not isinstance(sequence, str):
            return False

        # Standard nucleotide alphabet
        valid_nucleotides = set("ACGTU")
        sequence_upper = sequence.upper()

        return all(nt in valid_nucleotides for nt in sequence_upper)

    @staticmethod
    def validate_biologic_data(data: Dict[str, Any]) -> bool:
        """
        Validate biologic input data.

        Args:
            data: The biologic data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["name", "biologic_type"]
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_annotation_data(data: Dict[str, Any]) -> bool:
        """
        Validate annotation input data.

        Args:
            data: The annotation data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["sequences", "biologic_type"]
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_processing_input(data: Dict[str, Any]) -> bool:
        """
        Validate processing input data.

        Args:
            data: The processing data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["name", "biologic_type"]
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_response_data(data: Dict[str, Any]) -> bool:
        """
        Validate response data.

        Args:
            data: The response data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["success"]
        return all(field in data for field in required_fields)
