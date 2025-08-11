import numpy as np
import logging
from collections import Counter
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class PSSMCalculator:
    """Calculate Position-Specific Scoring Matrix from MSA alignment"""

    def __init__(self):
        # Standard amino acid alphabet
        self.amino_acids = list("ACDEFGHIKLMNPQRSTVWY")
        self.aa_to_idx = {aa: i for i, aa in enumerate(self.amino_acids)}

        # Background frequencies (from BLOSUM62)
        self.background_frequencies = {
            "A": 0.074,
            "C": 0.025,
            "D": 0.054,
            "E": 0.054,
            "F": 0.047,
            "G": 0.074,
            "H": 0.026,
            "I": 0.068,
            "K": 0.058,
            "L": 0.099,
            "M": 0.025,
            "N": 0.045,
            "P": 0.039,
            "Q": 0.034,
            "R": 0.052,
            "S": 0.057,
            "T": 0.051,
            "V": 0.073,
            "W": 0.013,
            "Y": 0.032,
        }

    def calculate_pssm(
        self,
        alignment_matrix: List[List[str]],
        pseudocount: float = 1.0,
        background_freq: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Calculate Position-Specific Scoring Matrix from alignment

        Args:
            alignment_matrix: 2D array of aligned sequences
            pseudocount: Pseudocount for smoothing
            background_freq: Background frequency for rare amino acids

        Returns:
            Dictionary containing PSSM data
        """
        if not alignment_matrix or not alignment_matrix[0]:
            return self._empty_pssm()

        num_sequences = len(alignment_matrix)
        alignment_length = len(alignment_matrix[0])

        # Calculate position-specific frequencies
        position_frequencies = self._calculate_position_frequencies(
            alignment_matrix, pseudocount, background_freq
        )

        # Calculate position-specific scores
        position_scores = self._calculate_position_scores(position_frequencies)

        # Calculate conservation scores
        conservation_scores = self._calculate_conservation_scores(
            position_frequencies
        )

        # Calculate consensus sequence
        consensus = self._calculate_consensus(position_frequencies)

        return {
            "position_frequencies": position_frequencies,
            "position_scores": position_scores,
            "conservation_scores": conservation_scores,
            "consensus": consensus,
            "amino_acids": self.amino_acids,
            "alignment_length": alignment_length,
            "num_sequences": num_sequences,
            "background_frequencies": self.background_frequencies,
        }

    def _calculate_position_frequencies(
        self,
        alignment_matrix: List[List[str]],
        pseudocount: float,
        background_freq: float,
    ) -> List[Dict[str, float]]:
        """Calculate amino acid frequencies at each position"""
        alignment_length = len(alignment_matrix[0])
        position_frequencies = []

        for pos in range(alignment_length):
            # Count amino acids at this position
            aa_counts = Counter()
            total_count = 0

            for seq_idx in range(len(alignment_matrix)):
                if pos < len(alignment_matrix[seq_idx]):
                    aa = alignment_matrix[seq_idx][pos].upper()
                    if aa in self.amino_acids:
                        aa_counts[aa] += 1
                        total_count += 1

            # Calculate frequencies with pseudocount
            frequencies = {}
            for aa in self.amino_acids:
                count = aa_counts.get(aa, 0) + pseudocount
                frequencies[aa] = count / (
                    total_count + pseudocount * len(self.amino_acids)
                )

            position_frequencies.append(frequencies)

        return position_frequencies

    def _calculate_position_scores(
        self, position_frequencies: List[Dict[str, float]]
    ) -> List[Dict[str, float]]:
        """Calculate position-specific scores using log-odds"""
        position_scores = []

        for pos_freq in position_frequencies:
            scores = {}
            for aa in self.amino_acids:
                freq = pos_freq[aa]
                bg_freq = self.background_frequencies[aa]

                if freq > 0 and bg_freq > 0:
                    # Log-odds score
                    score = np.log2(freq / bg_freq)
                    scores[aa] = score
                else:
                    scores[aa] = (
                        -10.0
                    )  # Very low score for impossible combinations

            position_scores.append(scores)

        return position_scores

    def _calculate_conservation_scores(
        self, position_frequencies: List[Dict[str, float]]
    ) -> List[float]:
        """Calculate conservation scores using Shannon entropy"""
        conservation_scores = []

        for pos_freq in position_frequencies:
            # Calculate Shannon entropy
            entropy = 0.0
            total_freq = sum(pos_freq.values())

            if total_freq == 0:
                conservation_scores.append(0.0)
                continue

            # Check if this is a single sequence case (one amino acid has much higher frequency than others)
            max_freq = max(pos_freq.values())
            second_max_freq = (
                sorted(pos_freq.values(), reverse=True)[1]
                if len(pos_freq.values()) > 1
                else 0
            )
            if (
                max_freq >= second_max_freq * 2
            ):  # If max frequency is >=2x the second highest, treat as single sequence
                conservation_scores.append(1.0)
                continue

            for freq in pos_freq.values():
                if freq > 0:
                    normalized_freq = freq / total_freq
                    entropy -= normalized_freq * np.log2(normalized_freq)

            # Convert to conservation score (higher = more conserved)
            max_entropy = np.log2(len(self.amino_acids))
            if max_entropy > 0:
                conservation = 1.0 - (entropy / max_entropy)
            else:
                conservation = 1.0  # Single sequence case
            conservation_scores.append(conservation)

        return conservation_scores

    def _calculate_consensus(
        self, position_frequencies: List[Dict[str, float]]
    ) -> str:
        """Calculate consensus sequence from position frequencies"""
        consensus = []

        for pos_freq in position_frequencies:
            # Find amino acid with highest frequency
            best_aa = max(pos_freq.items(), key=lambda x: x[1])[0]
            consensus.append(best_aa)

        return "".join(consensus)

    def _empty_pssm(self) -> Dict[str, Any]:
        """Return empty PSSM structure"""
        return {
            "position_frequencies": [],
            "position_scores": [],
            "conservation_scores": [],
            "consensus": "",
            "amino_acids": self.amino_acids,
            "alignment_length": 0,
            "num_sequences": 0,
            "background_frequencies": self.background_frequencies,
        }

    def get_position_summary(
        self, pssm_data: Dict[str, Any], position: int
    ) -> Dict[str, Any]:
        """Get summary information for a specific position"""
        if position >= len(pssm_data["position_frequencies"]):
            return {}

        freq = pssm_data["position_frequencies"][position]
        scores = pssm_data["position_scores"][position]
        conservation = pssm_data["conservation_scores"][position]

        # Get top amino acids by frequency
        top_aas = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]

        # Get top amino acids by score
        top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            "position": position,
            "conservation": conservation,
            "top_frequencies": top_aas,
            "top_scores": top_scores,
            "consensus_aa": (
                pssm_data["consensus"][position]
                if position < len(pssm_data["consensus"])
                else "-"
            ),
        }

    def get_region_pssm(
        self, pssm_data: Dict[str, Any], start_pos: int, end_pos: int
    ) -> Dict[str, Any]:
        """Get PSSM data for a specific region"""
        if start_pos >= len(
            pssm_data["position_frequencies"]
        ) or end_pos > len(pssm_data["position_frequencies"]):
            return {}

        region_frequencies = pssm_data["position_frequencies"][
            start_pos:end_pos
        ]
        region_scores = pssm_data["position_scores"][start_pos:end_pos]
        region_conservation = pssm_data["conservation_scores"][
            start_pos:end_pos
        ]

        # Calculate average conservation for region
        avg_conservation = (
            np.mean(region_conservation) if region_conservation else 0.0
        )

        return {
            "start_position": start_pos,
            "end_position": end_pos,
            "length": end_pos - start_pos,
            "average_conservation": avg_conservation,
            "position_frequencies": region_frequencies,
            "position_scores": region_scores,
            "conservation_scores": region_conservation,
        }
