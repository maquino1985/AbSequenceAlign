import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from typing import List, Tuple

from Bio import AlignIO, Align
from Bio.Align import substitution_matrices
from Bio.Align.Applications import MuscleCommandline

from .pssm_calculator import PSSMCalculator
from ..models.models import MSAResult, MSASequence, AlignmentMethod


class MSAEngine:
    """Multiple Sequence Alignment Engine supporting multiple methods"""

    def __init__(self):
        self.supported_methods = {
            AlignmentMethod.MUSCLE: self._align_muscle,
            AlignmentMethod.MAFFT: self._align_mafft,
            AlignmentMethod.CLUSTALO: self._align_clustalo,
            AlignmentMethod.PAIRWISE_GLOBAL: self._align_pairwise_global,
            AlignmentMethod.PAIRWISE_LOCAL: self._align_pairwise_local,
        }
        self.pssm_calculator = PSSMCalculator()

    def create_msa(
        self,
        sequences: List[Tuple[str, str]],
        method: AlignmentMethod = AlignmentMethod.MUSCLE,
    ) -> MSAResult:
        """
        Create multiple sequence alignment

        Args:
            sequences: List of (name, sequence) tuples
            method: Alignment method to use

        Returns:
            MSAResult with aligned sequences and metadata
        """
        if method not in self.supported_methods:
            raise ValueError(f"Unsupported alignment method: {method}")

        if not sequences:
            raise ValueError("No valid sequences provided")

        # Extract sequence data
        names = [seq[0] for seq in sequences]
        seqs = [seq[1] for seq in sequences]

        # Perform alignment
        aligned_sequences = self.supported_methods[method](seqs)

        # Create alignment matrix
        alignment_matrix = self._create_alignment_matrix(aligned_sequences)

        # Generate consensus
        consensus = self._generate_consensus(alignment_matrix)

        # Calculate PSSM
        pssm_data = self.pssm_calculator.calculate_pssm(alignment_matrix)

        # Create MSASequence objects
        msa_sequences = []
        for i, (name, original_seq, aligned_seq) in enumerate(
            zip(names, seqs, aligned_sequences)
        ):
            gaps = [j for j, char in enumerate(aligned_seq) if char == "-"]
            msa_seq = MSASequence(
                name=name,
                original_sequence=original_seq,
                aligned_sequence=aligned_seq,
                start_position=0,
                end_position=len(aligned_seq),
                gaps=gaps,
            )
            msa_sequences.append(msa_seq)

        # Create MSA result
        msa_result = MSAResult(
            msa_id=str(uuid.uuid4()),
            sequences=msa_sequences,
            alignment_matrix=alignment_matrix,
            consensus=consensus,
            alignment_method=method,
            created_at=datetime.now().isoformat(),
            metadata={
                "num_sequences": len(sequences),
                "alignment_length": (
                    len(aligned_sequences[0]) if aligned_sequences else 0
                ),
                "method": method.value,
                "pssm_data": pssm_data,
            },
        )

        return msa_result

    def _create_temp_fasta_file(self, sequences: List[str]) -> str:
        """Create a temporary FASTA file with the given sequences"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".fasta", delete=False
        ) as temp_file:
            for i, seq in enumerate(sequences):
                temp_file.write(f">seq_{i}\n{seq}\n")
            return temp_file.name

    def _cleanup_temp_files(self, *file_paths):
        """Clean up temporary files, ignoring FileNotFoundError"""
        for file_path in file_paths:
            if file_path:
                try:
                    os.unlink(file_path)
                except FileNotFoundError:
                    pass

    def _align_muscle(self, sequences: List[str]) -> List[str]:
        """Align sequences using MUSCLE"""
        if not sequences:
            return []

        temp_in_path = None
        temp_out_path = None

        try:
            # Create temporary files
            temp_in_path = self._create_temp_fasta_file(sequences)
            temp_out_path = tempfile.mktemp(suffix=".aln")

            # Run MUSCLE
            cmd = ["muscle", "-align", temp_in_path, "-output", temp_out_path]
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Read alignment
            alignment = AlignIO.read(temp_out_path, "fasta")
            aligned_sequences = [str(record.seq) for record in alignment]

            return aligned_sequences

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MUSCLE alignment failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in MUSCLE alignment: {e}")
        finally:
            self._cleanup_temp_files(temp_in_path, temp_out_path)

    def _align_mafft(self, sequences: List[str]) -> List[str]:
        """Align sequences using MAFFT"""
        temp_in_path = None

        try:
            # Create temporary FASTA file
            temp_in_path = self._create_temp_fasta_file(sequences)

            # Run MAFFT (outputs to stdout)
            cmd = ["mafft", "--auto", temp_in_path]
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True
            )

            # Parse MAFFT output from stdout
            aligned_sequences = result.stdout.strip().split("\n")
            sequences = []
            current_seq = ""
            for line in aligned_sequences:
                if line.startswith(">"):
                    if current_seq:
                        sequences.append(current_seq)
                    current_seq = ""
                else:
                    current_seq += line
            if current_seq:
                sequences.append(current_seq)

            return sequences

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MAFFT alignment failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in MAFFT alignment: {e}")
        finally:
            self._cleanup_temp_files(temp_in_path)

    def _align_clustalo(self, sequences: List[str]) -> List[str]:
        """Align sequences using Clustal Omega"""
        temp_in_path = None
        temp_out_path = None

        try:
            # Create temporary files
            temp_in_path = self._create_temp_fasta_file(sequences)
            temp_out_path = tempfile.mktemp(suffix=".aln")

            # Run Clustal Omega
            cmd = [
                "clustalo",
                "-i",
                temp_in_path,
                "-o",
                temp_out_path,
                "--outfmt=fasta",
                "--force",  # Force overwrite of existing output file
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Read alignment
            alignment = AlignIO.read(temp_out_path, "fasta")
            aligned_sequences = [str(record.seq) for record in alignment]

            return aligned_sequences

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Clustal Omega alignment failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in Clustal Omega alignment: {e}")
        finally:
            self._cleanup_temp_files(temp_in_path, temp_out_path)

    def _align_pairwise_global(self, sequences: List[str]) -> List[str]:
        """Align sequences using Biopython's built-in MSA capabilities as fallback"""
        if len(sequences) < 2:
            return sequences

        # Try external tools first, fall back to Biopython's MSA
        try:
            return self._align_muscle(sequences)
        except (
            RuntimeError,
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            # Fall back to Biopython's built-in MSA
            return self._biopython_msa_fallback(sequences, "global")

    def _align_pairwise_local(self, sequences: List[str]) -> List[str]:
        """Align sequences using Biopython's built-in MSA capabilities as fallback"""
        if len(sequences) < 2:
            return sequences

        # Try external tools first, fall back to Biopython's MSA
        try:
            return self._align_muscle(sequences)
        except (
            RuntimeError,
            FileNotFoundError,
            subprocess.CalledProcessError,
        ):
            # Fall back to Biopython's built-in MSA
            return self._biopython_msa_fallback(sequences, "local")

    def _biopython_msa_fallback(
        self, sequences: List[str], mode: str
    ) -> List[str]:
        """Use Biopython's built-in MSA capabilities as fallback"""
        if len(sequences) < 2:
            return sequences

        # For small datasets, use progressive alignment
        if len(sequences) <= 10:
            return self._progressive_alignment_biopython(sequences, mode)
        else:
            # For larger datasets, try to use MUSCLE through Biopython's wrapper
            try:
                return self._muscle_biopython_wrapper(sequences)
            except (
                RuntimeError,
                FileNotFoundError,
                subprocess.CalledProcessError,
            ):
                # Final fallback to progressive alignment
                return self._progressive_alignment_biopython(sequences, mode)

    def _progressive_alignment_biopython(
        self, sequences: List[str], mode: str
    ) -> List[str]:
        """Use Biopython's progressive alignment approach"""
        if len(sequences) < 2:
            return sequences

        # Initialize with first sequence
        aligned_sequences = [sequences[0]]

        aligner = Align.PairwiseAligner()
        aligner.mode = mode
        aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
        aligner.open_gap_score = -10
        aligner.extend_gap_score = -0.5

        # Progressive alignment: align each new sequence with the profile of existing sequences
        for i in range(1, len(sequences)):
            current_seq = sequences[i]

            # Align current sequence with the first sequence (as a simple profile)
            target_seq = aligned_sequences[0]

            alignments = aligner.align(target_seq, current_seq)
            if alignments:
                alignment = alignments[0]
                target, query = alignment.target, alignment.query

                # Ensure both sequences have the same length
                max_length = max(len(target), len(query))
                target_padded = target + "-" * (max_length - len(target))
                query_padded = query + "-" * (max_length - len(query))

                # Update all existing sequences with padding
                for j in range(len(aligned_sequences)):
                    seq = aligned_sequences[j]
                    aligned_sequences[j] = seq + "-" * (max_length - len(seq))

                # Add the new aligned sequence
                aligned_sequences.append(query_padded)

                # Update the target sequence
                aligned_sequences[0] = target_padded

        return aligned_sequences

    def _muscle_biopython_wrapper(self, sequences: List[str]) -> List[str]:
        """Use Biopython's MUSCLE wrapper as an additional fallback"""

        # Create temporary files
        temp_in_path = self._create_temp_fasta_file(sequences)
        temp_out_path = temp_in_path.replace(".fasta", "_aligned.fasta")

        try:
            # Run MUSCLE through Biopython's wrapper
            muscle_cline = MuscleCommandline(
                input=temp_in_path, out=temp_out_path, outfmt="fasta"
            )

            # Execute the command
            stdout, stderr = muscle_cline()

            # Read the alignment
            from Bio import AlignIO

            alignment = AlignIO.read(temp_out_path, "fasta")
            aligned_sequences = [str(record.seq) for record in alignment]

            return aligned_sequences

        except Exception as e:
            raise RuntimeError(f"MUSCLE alignment failed: {e}")
        finally:
            self._cleanup_temp_files(temp_in_path, temp_out_path)

    def _create_alignment_matrix(
        self, aligned_sequences: List[str]
    ) -> List[List[str]]:
        """Create 2D alignment matrix"""
        if not aligned_sequences:
            return []

        matrix = []
        for seq in aligned_sequences:
            matrix.append(list(seq))

        return matrix

    def _generate_consensus(self, alignment_matrix: List[List[str]]) -> str:
        """Generate consensus sequence from alignment matrix"""
        if not alignment_matrix:
            return ""

        consensus = []
        num_sequences = len(alignment_matrix)

        # Find the maximum length of any sequence
        max_length = (
            max(len(seq) for seq in alignment_matrix)
            if alignment_matrix
            else 0
        )

        for col in range(max_length):
            # Count amino acids at this position
            aa_counts = {}
            for row in range(num_sequences):
                if col < len(alignment_matrix[row]):
                    aa = alignment_matrix[row][col]
                    if aa != "-":  # Skip gaps
                        aa_counts[aa] = aa_counts.get(aa, 0) + 1

            if aa_counts:
                # Find most common amino acid
                most_common = max(aa_counts.items(), key=lambda x: x[1])
                consensus.append(most_common[0])
            else:
                # All gaps at this position
                consensus.append("-")

        return "".join(consensus)
