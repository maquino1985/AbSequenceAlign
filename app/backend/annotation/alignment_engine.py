import os
import subprocess
import tempfile
from typing import List, Dict, Any

from Bio.Align import PairwiseAligner, substitution_matrices
from backend.logger import logger
from backend.models.models import AlignmentMethod, NumberingScheme


class AlignmentEngine:
    """Handles sequence alignment using various algorithms"""

    def __init__(self):
        # Load substitution matrices as a dictionary
        self.available_matrices = {}
        for matrix_name in substitution_matrices.load():
            self.available_matrices[matrix_name] = substitution_matrices.load(
                matrix_name
            )

    def align_sequences(
        self,
        sequences: List[str],
        method: AlignmentMethod,
        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
        gap_open: float = -10.0,
        gap_extend: float = -0.5,
        matrix: str = "BLOSUM62",
    ) -> Dict[str, Any]:
        """
        Perform sequence alignment using specified method

        Args:
            sequences: List of protein sequences
            method: Alignment method to use
            numbering_scheme: Numbering scheme (for antibody-aware alignment)
            gap_open: Gap opening penalty
            gap_extend: Gap extension penalty
            matrix: Substitution matrix name

        Returns:
            Dictionary with alignment results
        """
        if len(sequences) < 2:
            raise ValueError("At least 2 sequences required for alignment")

        # Validate method
        if not isinstance(method, AlignmentMethod):
            raise ValueError(f"Unsupported alignment method: {method}")

        # Validate matrix
        if matrix not in self.available_matrices:
            raise ValueError(f"Unsupported substitution matrix: {matrix}")

        try:
            if method == AlignmentMethod.PAIRWISE_GLOBAL:
                return self._pairwise_global_alignment(
                    sequences, gap_open, gap_extend, matrix
                )
            elif method == AlignmentMethod.PAIRWISE_LOCAL:
                return self._pairwise_local_alignment(
                    sequences, gap_open, gap_extend, matrix
                )
            elif method in [
                AlignmentMethod.MUSCLE,
                AlignmentMethod.MAFFT,
                AlignmentMethod.CLUSTALO,
            ]:
                return self._external_msa_alignment(
                    sequences, method, gap_open, gap_extend, matrix
                )
            elif method == AlignmentMethod.CUSTOM_ANTIBODY:
                return self._antibody_aware_alignment(
                    sequences, numbering_scheme, gap_open, gap_extend, matrix
                )
            else:
                raise ValueError(f"Unsupported alignment method: {method}")

        except ValueError as e:
            # Re-raise validation errors
            raise e
        except Exception as e:
            logger.error(f"Alignment failed: {e}")
            raise RuntimeError(f"Alignment failed: {e}")

    def _pairwise_global_alignment(
        self,
        sequences: List[str],
        gap_open: float,
        gap_extend: float,
        matrix: str,
    ) -> Dict[str, Any]:
        """Perform global pairwise alignment"""
        if len(sequences) != 2:
            raise ValueError("Pairwise alignment requires exactly 2 sequences")

        # Load substitution matrix
        if matrix in self.available_matrices:
            scoring_matrix = self.available_matrices[matrix]
        else:
            scoring_matrix = self.available_matrices["BLOSUM62"]

        # Create aligner with scoring matrix and gap penalties
        aligner = PairwiseAligner()
        aligner.mode = "global"
        aligner.substitution_matrix = scoring_matrix
        aligner.open_gap_score = gap_open
        aligner.extend_gap_score = gap_extend

        # Perform alignment
        alignments = list(aligner.align(sequences[0], sequences[1]))
        if not alignments:
            raise RuntimeError("No alignment found")

        # Get best alignment
        best_alignment = alignments[0]
        alignment_str = str(best_alignment)

        # Parse alignment string to extract sequences
        seq_a, seq_b = self._parse_alignment_string(alignment_str)

        # Calculate statistics
        score = best_alignment.score
        identity = self._calculate_identity(seq_a, seq_b)

        # Calculate length of aligned sequences
        aligned_length = len(seq_a)

        return {
            "method": "pairwise_global",
            "alignment": str(best_alignment),
            "score": score,
            "identity": identity,
            "length": aligned_length,
            "gaps": seq_a.count("-") + seq_b.count("-"),
        }

    def _pairwise_local_alignment(
        self,
        sequences: List[str],
        gap_open: float,
        gap_extend: float,
        matrix: str,
    ) -> Dict[str, Any]:
        """Perform local pairwise alignment"""
        if len(sequences) != 2:
            raise ValueError("Pairwise alignment requires exactly 2 sequences")

        # Load substitution matrix
        if matrix in self.available_matrices:
            scoring_matrix = self.available_matrices[matrix]
        else:
            scoring_matrix = self.available_matrices["BLOSUM62"]

        # Create aligner with scoring matrix and gap penalties
        aligner = PairwiseAligner()
        aligner.mode = "local"
        aligner.substitution_matrix = scoring_matrix
        aligner.open_gap_score = gap_open
        aligner.extend_gap_score = gap_extend

        # Perform alignment
        alignments = list(aligner.align(sequences[0], sequences[1]))
        if not alignments:
            raise RuntimeError("No alignment found")

        # Get best alignment
        best_alignment = alignments[0]
        alignment_str = str(best_alignment)

        # Parse alignment string to extract sequences
        seq_a, seq_b = self._parse_alignment_string(alignment_str)

        # Calculate statistics
        score = best_alignment.score
        identity = self._calculate_identity(seq_a, seq_b)

        # Calculate length of aligned sequences
        aligned_length = len(seq_a)

        return {
            "method": "pairwise_local",
            "alignment": str(best_alignment),
            "score": score,
            "identity": identity,
            "length": aligned_length,
            "gaps": seq_a.count("-") + seq_b.count("-"),
        }

    def _external_msa_alignment(
        self,
        sequences: List[str],
        method: AlignmentMethod,
        gap_open: float,
        gap_extend: float,
        matrix: str,
    ) -> Dict[str, Any]:
        """Perform MSA using external tools"""

        # Create temporary FASTA file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as temp_fasta:
            for i, seq in enumerate(sequences):
                temp_fasta.write(f">sequence_{i + 1}\n{seq}\n")
            temp_fasta_path = temp_fasta.name

        # Create temporary output file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".aln", delete=False
        ) as temp_output:
            temp_output_path = temp_output.name

        try:
            if method == AlignmentMethod.MUSCLE:
                cmd = [
                    "muscle",
                    "-align",
                    temp_fasta_path,
                    "-output",
                    temp_output_path,
                ]
            elif method == AlignmentMethod.MAFFT:
                cmd = [
                    "mafft",
                    "--localpair",
                    "--maxiterate",
                    "1000",
                    temp_fasta_path,
                ]
            elif method == AlignmentMethod.CLUSTALO:
                cmd = [
                    "clustalo",
                    "-i",
                    temp_fasta_path,
                    "-o",
                    temp_output_path,
                    "--outfmt=fasta",
                ]
            else:
                raise ValueError(f"Unsupported MSA method: {method}")

            # Run external tool
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"External alignment failed: {result.stderr}"
                )

            # Read alignment result
            if method == AlignmentMethod.MAFFT:
                # MAFFT outputs to stdout
                alignment_content = result.stdout
            else:
                # Other tools output to file
                with open(temp_output_path, "r") as f:
                    alignment_content = f.read()

            # Calculate statistics
            aligned_sequences = self._parse_alignment(alignment_content)
            identity = self._calculate_msa_identity(aligned_sequences)

            return {
                "method": method.value,
                "alignment": alignment_content,
                "identity": identity,
                "length": (
                    len(aligned_sequences[0]) if aligned_sequences else 0
                ),
                "sequences": len(aligned_sequences),
            }

        finally:
            # Clean up temporary files
            if os.path.exists(temp_fasta_path):
                os.unlink(temp_fasta_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def _antibody_aware_alignment(
        self,
        sequences: List[str],
        numbering_scheme: NumberingScheme,
        gap_open: float,
        gap_extend: float,
        matrix: str,
    ) -> Dict[str, Any]:
        """
        Perform antibody-aware alignment using numbered positions

        This is a simplified version. In practice, you would:
        1. Number sequences with ANARCI
        2. Align based on consensus-numbered positions
        3. Optionally align CDRs separately
        """

        # For now, fall back to MUSCLE alignment
        # In a full implementation, you would integrate with ANARCI numbering
        logger.warning(
            "Antibody-aware alignment not fully implemented, using MUSCLE fallback"
        )
        return self._external_msa_alignment(
            sequences, AlignmentMethod.MUSCLE, gap_open, gap_extend, matrix
        )

    def _parse_alignment_string(self, alignment_str: str) -> tuple[str, str]:
        """Parse Biopython alignment string to extract sequences"""
        lines = alignment_str.split("\n")
        seq_a = ""
        seq_b = ""

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if (
                line.startswith("target")
                and i + 2 < len(lines)
                and "query" in lines[i + 2]
            ):
                # Extract target sequence (first sequence)
                target_line = line
                query_line = lines[i + 2]

                # Parse target sequence - it's the part between the position numbers
                target_parts = target_line.split()
                if len(target_parts) >= 3:
                    seq_a += target_parts[2]  # The sequence part

                # Parse query sequence - it's the part between the position numbers
                query_parts = query_line.split()
                if len(query_parts) >= 3:
                    seq_b += query_parts[2]  # The sequence part

                i += 3  # Skip the middle line with alignment indicators
            else:
                i += 1

        # If we didn't find the sequences in the expected format, try fallback
        if not seq_a or not seq_b:
            # Look for lines that contain only sequence characters
            for line in lines:
                line = line.strip()
                if line and all(c in "ACDEFGHIKLMNPQRSTVWY-" for c in line):
                    if not seq_a:
                        seq_a = line
                    elif not seq_b:
                        seq_b = line
                        break

        return seq_a, seq_b

    def _calculate_identity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence identity between two aligned sequences"""
        from Bio.Seq import Seq

        # For aligned sequences, they should be the same length
        # But handle cases where they might not be (e.g., test cases)
        if len(seq1) != len(seq2):
            # If lengths differ, pad the shorter one with gaps
            max_len = max(len(seq1), len(seq2))
            seq1 = seq1.ljust(max_len, "-")
            seq2 = seq2.ljust(max_len, "-")

        # Convert to Bio.Seq objects for validation
        seq1_obj = Seq(seq1)
        seq2_obj = Seq(seq2)

        # Calculate identity: matches / (non-gap positions)
        matches = 0
        total_positions = 0

        for a, b in zip(seq1_obj, seq2_obj):
            if a != "-" and b != "-":
                total_positions += 1
                if a == b:
                    matches += 1

        return matches / total_positions if total_positions > 0 else 0.0

    def _calculate_msa_identity(self, aligned_sequences: List[str]) -> float:
        """Calculate average identity across MSA"""
        if len(aligned_sequences) < 2:
            return 0.0

        total_identity = 0.0
        comparisons = 0

        for i in range(len(aligned_sequences)):
            for j in range(i + 1, len(aligned_sequences)):
                identity = self._calculate_identity(
                    aligned_sequences[i], aligned_sequences[j]
                )
                total_identity += identity
                comparisons += 1

        return total_identity / comparisons if comparisons > 0 else 0.0

    def _parse_alignment(self, alignment_content: str) -> List[str]:
        """Parse alignment content and extract sequences"""
        sequences = []
        current_seq = ""

        for line in alignment_content.split("\n"):
            if line.startswith(">"):
                if current_seq:
                    sequences.append(current_seq)
                current_seq = ""
            elif line.strip():
                current_seq += line.strip()

        if current_seq:
            sequences.append(current_seq)

        return sequences

    def _map_position_to_aligned(
        self, orig_pos: int, original_seq: str, aligned_seq: str
    ) -> int:
        """
        Map a position from original sequence to aligned sequence

        Args:
            orig_pos: Position in original sequence (0-based)
            original_seq: Original sequence
            aligned_seq: Aligned sequence with gaps

        Returns:
            Position in aligned sequence (0-based)
        """
        if orig_pos >= len(original_seq):
            return len(aligned_seq) - 1

        # Count gaps up to the target position
        gap_count = 0
        orig_count = 0

        for i, char in enumerate(aligned_seq):
            if char == "-":
                gap_count += 1
            else:
                if orig_count == orig_pos:
                    return i
                orig_count += 1

        return len(aligned_seq) - 1
