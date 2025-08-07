import logging
import os
import subprocess
import tempfile
from typing import List, Dict, Any

from Bio.Align import PairwiseAligner, substitution_matrices

from app.models.models import AlignmentMethod, NumberingScheme

logger = logging.getLogger(__name__)


class AlignmentEngine:
    """Handles sequence alignment using various algorithms"""

    def __init__(self):
        self.available_matrices = substitution_matrices.load()

    def align_sequences(self, sequences: List[str],
                        method: AlignmentMethod,
                        numbering_scheme: NumberingScheme = NumberingScheme.IMGT,
                        gap_open: float = -10.0,
                        gap_extend: float = -0.5,
                        matrix: str = "BLOSUM62") -> Dict[str, Any]:
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

        try:
            if method == AlignmentMethod.PAIRWISE_GLOBAL:
                return self._pairwise_global_alignment(sequences, gap_open, gap_extend, matrix)
            elif method == AlignmentMethod.PAIRWISE_LOCAL:
                return self._pairwise_local_alignment(sequences, gap_open, gap_extend, matrix)
            elif method in [AlignmentMethod.MUSCLE, AlignmentMethod.MAFFT, AlignmentMethod.CLUSTALO]:
                return self._external_msa_alignment(sequences, method, gap_open, gap_extend, matrix)
            elif method == AlignmentMethod.CUSTOM_ANTIBODY:
                return self._antibody_aware_alignment(sequences, numbering_scheme, gap_open, gap_extend, matrix)
            else:
                raise ValueError(f"Unsupported alignment method: {method}")

        except Exception as e:
            logger.error(f"Alignment failed: {e}")
            raise RuntimeError(f"Alignment failed: {e}")

    def _pairwise_global_alignment(self, sequences: List[str],
                                   gap_open: float, gap_extend: float,
                                   matrix: str) -> Dict[str, Any]:
        """Perform global pairwise alignment"""
        if len(sequences) != 2:
            raise ValueError("Pairwise alignment requires exactly 2 sequences")

        # Load substitution matrix
        if matrix in self.available_matrices:
            scoring_matrix = self.available_matrices[matrix]
        else:
            scoring_matrix = self.available_matrices["BLOSUM62"]

        # Perform alignment
        alignments = PairwiseAligner.align.globalds(
            sequences[0], sequences[1],
            scoring_matrix, gap_open, gap_extend
        )
        

        if not alignments:
            raise RuntimeError("No alignment found")

        best_alignment = alignments[0]
        best_alignment.format()

        # Calculate statistics
        score = best_alignment.score
        identity = self._calculate_identity(best_alignment.seqA, best_alignment.seqB)

        return {
            "method": "pairwise_global",
            "alignment": best_alignment,
            "score": score,
            "identity": identity,
            "length": len(best_alignment.seqA),
            "gaps": best_alignment.seqA.count("-") + best_alignment.seqB.count("-")
        }

    def _pairwise_local_alignment(self, sequences: List[str],
                                  gap_open: float, gap_extend: float,
                                  matrix: str) -> Dict[str, Any]:
        """Perform local pairwise alignment"""
        if len(sequences) != 2:
            raise ValueError("Pairwise alignment requires exactly 2 sequences")

        # Load substitution matrix
        if matrix in self.available_matrices:
            scoring_matrix = self.available_matrices[matrix]
        else:
            scoring_matrix = self.available_matrices["BLOSUM62"]

        # Perform alignment
        alignments = PairwiseAligner.align.localds(
            sequences[0], sequences[1],
            scoring_matrix, gap_open, gap_extend
        )

        if not alignments:
            raise RuntimeError("No alignment found")

        best_alignment = alignments[0]

        # Calculate statistics
        score = best_alignment.score
        identity = self._calculate_identity(best_alignment.seqA, best_alignment.seqB)

        return {
            "method": "pairwise_local",
            "alignment": best_alignment.format(),
            "score": score,
            "identity": identity,
            "length": len(best_alignment.seqA),
            "gaps": best_alignment.seqA.count("-") + best_alignment.seqB.count("-")
        }

    def _external_msa_alignment(self, sequences: List[str],
                                method: AlignmentMethod,
                                gap_open: float, gap_extend: float,
                                matrix: str) -> Dict[str, Any]:
        """Perform MSA using external tools"""

        # Create temporary FASTA file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_fasta:
            for i, seq in enumerate(sequences):
                temp_fasta.write(f">sequence_{i + 1}\n{seq}\n")
            temp_fasta_path = temp_fasta.name

        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.aln', delete=False) as temp_output:
            temp_output_path = temp_output.name

        try:
            if method == AlignmentMethod.MUSCLE:
                cmd = [
                    "muscle",
                    "-in", temp_fasta_path,
                    "-out", temp_output_path,
                    "-gapopen", str(gap_open),
                    "-gapextend", str(gap_extend)
                ]
            elif method == AlignmentMethod.MAFFT:
                cmd = [
                    "mafft",
                    "--localpair",
                    "--maxiterate", "1000",
                    temp_fasta_path
                ]
            elif method == AlignmentMethod.CLUSTALO:
                cmd = [
                    "clustalo",
                    "-i", temp_fasta_path,
                    "-o", temp_output_path,
                    "--outfmt=fasta"
                ]
            else:
                raise ValueError(f"Unsupported MSA method: {method}")

            # Run external tool
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise RuntimeError(f"External alignment failed: {result.stderr}")

            # Read alignment result
            if method == AlignmentMethod.MAFFT:
                # MAFFT outputs to stdout
                alignment_content = result.stdout
            else:
                # Other tools output to file
                with open(temp_output_path, 'r') as f:
                    alignment_content = f.read()

            # Calculate statistics
            aligned_sequences = self._parse_alignment(alignment_content)
            identity = self._calculate_msa_identity(aligned_sequences)

            return {
                "method": method.value,
                "alignment": alignment_content,
                "identity": identity,
                "length": len(aligned_sequences[0]) if aligned_sequences else 0,
                "sequences": len(aligned_sequences)
            }

        finally:
            # Clean up temporary files
            if os.path.exists(temp_fasta_path):
                os.unlink(temp_fasta_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    def _antibody_aware_alignment(self, sequences: List[str],
                                  numbering_scheme: NumberingScheme,
                                  gap_open: float, gap_extend: float,
                                  matrix: str) -> Dict[str, Any]:
        """
        Perform antibody-aware alignment using numbered positions
        
        This is a simplified version. In practice, you would:
        1. Number sequences with ANARCI
        2. Align based on consensus-numbered positions
        3. Optionally align CDRs separately
        """

        # For now, fall back to MUSCLE alignment
        # In a full implementation, you would integrate with ANARCI numbering
        logger.warning("Antibody-aware alignment not fully implemented, using MUSCLE fallback")
        return self._external_msa_alignment(sequences, AlignmentMethod.MUSCLE, gap_open, gap_extend, matrix)

    def _calculate_identity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence identity between two aligned sequences"""
        if len(seq1) != len(seq2):
            return 0.0

        matches = sum(1 for a, b in zip(seq1, seq2) if a == b and a != '-')
        total = sum(1 for a, b in zip(seq1, seq2) if a != '-' or b != '-')

        return matches / total if total > 0 else 0.0

    def _calculate_msa_identity(self, aligned_sequences: List[str]) -> float:
        """Calculate average identity across MSA"""
        if len(aligned_sequences) < 2:
            return 0.0

        total_identity = 0.0
        comparisons = 0

        for i in range(len(aligned_sequences)):
            for j in range(i + 1, len(aligned_sequences)):
                identity = self._calculate_identity(aligned_sequences[i], aligned_sequences[j])
                total_identity += identity
                comparisons += 1

        return total_identity / comparisons if comparisons > 0 else 0.0

    def _parse_alignment(self, alignment_content: str) -> List[str]:
        """Parse alignment content and extract sequences"""
        sequences = []
        current_seq = ""

        for line in alignment_content.split('\n'):
            if line.startswith('>'):
                if current_seq:
                    sequences.append(current_seq)
                current_seq = ""
            elif line.strip():
                current_seq += line.strip()

        if current_seq:
            sequences.append(current_seq)

        return sequences
