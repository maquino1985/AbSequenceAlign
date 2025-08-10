from io import StringIO
from typing import List, Dict, Tuple, Optional, Any

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from ..logger import logger


class SequenceProcessor:
    """Handles FASTA parsing, validation, and sequence processing"""

    def __init__(self):
        self.valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")

    def parse_fasta(self, fasta_content: str) -> List[SeqRecord]:
        """
        Parse FASTA content and return list of SeqRecord objects

        Args:
            fasta_content: String containing FASTA format sequences

        Returns:
            List of BioPython SeqRecord objects

        Raises:
            ValueError: If FASTA parsing fails
        """
        try:
            fasta_io = StringIO(fasta_content)
            records = list(SeqIO.parse(fasta_io, "fasta"))

            if not records:
                raise ValueError("No sequences found in FASTA content")

            return records
        except Exception as e:
            logger.error(f"Failed to parse FASTA: {e}")
            raise ValueError(f"Invalid FASTA format: {e}")

    def validate_sequence(self, sequence: str) -> Tuple[bool, str]:
        """
        Validate if a sequence contains valid amino acids

        Args:
            sequence: Protein sequence string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sequence:
            return False, "Empty sequence"

        # Convert to uppercase and remove whitespace
        clean_seq = sequence.upper().replace(" ", "").replace("\n", "")

        # Check for invalid characters
        invalid_chars = set(clean_seq) - self.valid_amino_acids
        if invalid_chars:
            return False, f"Invalid amino acids found: {invalid_chars}"

        # Check minimum length (sequences should be at least 15 AA for HMMER3 compatibility)
        if len(clean_seq) < 15:
            return (
                False,
                f"Sequence too short ({len(clean_seq)} AA). Minimum 15 AA required.",
            )

        return True, ""

    def validate_sequences(
        self, sequences: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Validate a list of sequences

        Args:
            sequences: List of protein sequences

        Returns:
            Tuple of (valid_sequences, error_messages)
        """
        valid_sequences = []
        error_messages = []

        for i, seq in enumerate(sequences):
            is_valid, error = self.validate_sequence(seq)
            if is_valid:
                valid_sequences.append(seq)
            else:
                error_messages.append(f"Sequence {i + 1}: {error}")

        return valid_sequences, error_messages

    def extract_sequences_from_fasta(self, fasta_content: str) -> List[str]:
        """
        Extract sequences from FASTA content

        Args:
            fasta_content: FASTA format string

        Returns:
            List of sequence strings
        """
        records = self.parse_fasta(fasta_content)
        return [str(record.seq) for record in records]

    def format_fasta(
        self, sequences: List[str], names: Optional[List[str]] = None
    ) -> str:
        """
        Format sequences as FASTA string

        Args:
            sequences: List of protein sequences
            names: Optional list of sequence names

        Returns:
            FASTA format string
        """
        if names is None:
            names = [f"sequence_{i + 1}" for i in range(len(sequences))]

        fasta_lines = []
        for name, seq in zip(names, sequences):
            fasta_lines.append(f">{name}")
            # Split long sequences into lines of 80 characters
            for i in range(0, len(seq), 80):
                fasta_lines.append(seq[i:i + 80])

        return "\n".join(fasta_lines)

    def get_sequence_statistics(self, sequences: List[str]) -> Dict[str, Any]:
        """
        Calculate basic statistics for a set of sequences

        Args:
            sequences: List of protein sequences

        Returns:
            Dictionary with sequence statistics
        """
        if not sequences:
            return {}

        lengths = [len(seq) for seq in sequences]

        return {
            "total_sequences": len(sequences),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "avg_length": sum(lengths) / len(lengths),
            "total_length": sum(lengths),
        }
