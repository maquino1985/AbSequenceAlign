"""
Pure validation service for biologic data validation.
"""

from typing import Dict, Any
from backend.domain.entities import BiologicEntity, BiologicChain
from backend.logger import logger


class ValidationService:
    """Service for validating biologic data"""

    def __init__(self):
        """Initialize the validation service"""
        pass

    def validate_sequence(self, sequence: BiologicEntity) -> bool:
        """
        Validate a biologic sequence.

        Args:
            sequence: The biologic sequence to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not sequence:
                logger.error("Sequence is None or empty")
                return False

            if not sequence.name:
                logger.error("Sequence name is required")
                return False

            if not sequence.chains:
                logger.error("Sequence must have at least one chain")
                return False

            # Validate each chain
            for chain in sequence.chains:
                if not self.validate_chain(chain):
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating sequence: {e}")
            return False

    def validate_chain(self, chain: BiologicChain) -> bool:
        """
        Validate a biologic chain.

        Args:
            chain: The biologic chain to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not chain:
                logger.error("Chain is None or empty")
                return False

            if not chain.name:
                logger.error("Chain name is required")
                return False

            if not chain.sequences:
                logger.error("Chain sequences are required")
                return False

            # Validate each sequence in the chain
            for sequence in chain.sequences:
                if not self.validate_amino_acid_sequence(
                    sequence.sequence_data
                ):
                    logger.error(
                        f"Invalid amino acid sequence in chain {chain.name}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating chain: {e}")
            return False

    def validate_sequences(self, sequences: Dict[str, Any]) -> bool:
        """
        Validate multiple sequences.

        Args:
            sequences: Dictionary of sequences to validate

        Returns:
            True if all valid, False otherwise
        """
        try:
            if not sequences:
                logger.error("Sequences dictionary is empty")
                return False

            for name, sequence_data in sequences.items():
                if not name:
                    logger.error("Sequence name is required")
                    return False

                # Convert to BiologicEntity if needed
                if isinstance(sequence_data, BiologicEntity):
                    if not self.validate_sequence(sequence_data):
                        return False
                else:
                    logger.error(f"Invalid sequence data type for {name}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating sequences: {e}")
            return False

    def validate_amino_acid_sequence(self, sequence: str) -> bool:
        """
        Validate an amino acid sequence.

        Args:
            sequence: The amino acid sequence to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not sequence:
                logger.error("Amino acid sequence is empty")
                return False

            # Check for valid amino acid characters
            valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
            sequence_upper = sequence.upper()

            for char in sequence_upper:
                if char not in valid_aa:
                    logger.error(f"Invalid amino acid character: {char}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating amino acid sequence: {e}")
            return False

    def validate_request_data(self, request_data: Dict[str, Any]) -> bool:
        """
        Validate API request data.

        Args:
            request_data: The request data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not request_data:
                logger.error("Request data is empty")
                return False

            # Check for required fields
            required_fields = ["sequences"]
            for field in required_fields:
                if field not in request_data:
                    logger.error(f"Missing required field: {field}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating request data: {e}")
            return False
