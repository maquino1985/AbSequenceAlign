import subprocess
import tempfile
import os
import uuid
from typing import List, Dict, Any, Tuple
from datetime import datetime
from Bio import AlignIO, Align
from Bio.Align.Applications import MuscleCommandline, ClustalOmegaCommandline
from Bio.Align.Applications import MafftCommandline
from Bio.Align import substitution_matrices
from Bio.Align.Applications import ClustalwCommandline
import numpy as np

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
    
    def create_msa(self, sequences: List[Tuple[str, str]], method: AlignmentMethod = AlignmentMethod.MUSCLE) -> MSAResult:
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
        
        # Create MSASequence objects
        msa_sequences = []
        for i, (name, original_seq, aligned_seq) in enumerate(zip(names, seqs, aligned_sequences)):
            gaps = [j for j, char in enumerate(aligned_seq) if char == '-']
            msa_seq = MSASequence(
                name=name,
                original_sequence=original_seq,
                aligned_sequence=aligned_seq,
                start_position=0,
                end_position=len(aligned_seq),
                gaps=gaps
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
                "alignment_length": len(aligned_sequences[0]) if aligned_sequences else 0,
                "method": method.value
            }
        )
        
        return msa_result
    
    def _align_muscle(self, sequences: List[str]) -> List[str]:
        """Align sequences using MUSCLE"""
        if not sequences:
            return []
        
        try:
            # Create temporary FASTA file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_in:
                for i, seq in enumerate(sequences):
                    temp_in.write(f">seq_{i}\n{seq}\n")
                temp_in_path = temp_in.name
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.aln', delete=False) as temp_out:
                temp_out_path = temp_out.name
            
            # Run MUSCLE with proper command line for version 5.x
            cmd = ["muscle", "-align", temp_in_path, "-output", temp_out_path]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Read alignment
            alignment = AlignIO.read(temp_out_path, "fasta")
            aligned_sequences = [str(record.seq) for record in alignment]
            
            # Cleanup
            os.unlink(temp_in_path)
            os.unlink(temp_out_path)
            
            return aligned_sequences
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MUSCLE alignment failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in MUSCLE alignment: {e}")
    
    def _align_mafft(self, sequences: List[str]) -> List[str]:
        """Align sequences using MAFFT"""
        try:
            # Create temporary FASTA file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_in:
                for i, seq in enumerate(sequences):
                    temp_in.write(f">seq_{i}\n{seq}\n")
                temp_in_path = temp_in.name
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.aln', delete=False) as temp_out:
                temp_out_path = temp_out.name
            
            # Run MAFFT with proper command line
            cmd = ["mafft", "--auto", temp_in_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            aligned_sequences = result.stdout.strip().split('\n')
            # Filter out header lines and join sequences
            sequences = []
            current_seq = ""
            for line in aligned_sequences:
                if line.startswith('>'):
                    if current_seq:
                        sequences.append(current_seq)
                    current_seq = ""
                else:
                    current_seq += line
            if current_seq:
                sequences.append(current_seq)
            
            # Cleanup
            os.unlink(temp_in_path)
            
            return sequences
            
            # Read alignment
            alignment = AlignIO.read(temp_out_path, "fasta")
            aligned_sequences = [str(record.seq) for record in alignment]
            
            # Cleanup
            os.unlink(temp_in_path)
            os.unlink(temp_out_path)
            
            return aligned_sequences
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"MAFFT alignment failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in MAFFT alignment: {e}")
    
    def _align_clustalo(self, sequences: List[str]) -> List[str]:
        """Align sequences using Clustal Omega"""
        try:
            # Create temporary FASTA file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as temp_in:
                for i, seq in enumerate(sequences):
                    temp_in.write(f">seq_{i}\n{seq}\n")
                temp_in_path = temp_in.name
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.aln', delete=False) as temp_out:
                temp_out_path = temp_out.name
            
            # Run Clustal Omega with proper command line
            cmd = ["clustalo", "-i", temp_in_path, "-o", temp_out_path, "--outfmt=fasta"]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Read alignment
            alignment = AlignIO.read(temp_out_path, "fasta")
            aligned_sequences = [str(record.seq) for record in alignment]
            
            # Cleanup
            os.unlink(temp_in_path)
            os.unlink(temp_out_path)
            
            return aligned_sequences
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Clustal Omega alignment failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in Clustal Omega alignment: {e}")
    
    def _align_pairwise_global(self, sequences: List[str]) -> List[str]:
        """Align sequences using BioPython's pairwise global alignment"""
        if len(sequences) < 2:
            return sequences
        
        # Use progressive alignment for multiple sequences
        aligned_sequences = [sequences[0]]
        
        for i in range(1, len(sequences)):
            # Align current sequence with the first aligned sequence
            aligner = Align.PairwiseAligner()
            aligner.mode = 'global'
            aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
            aligner.open_gap_score = -10
            aligner.extend_gap_score = -0.5
            
            alignments = aligner.align(aligned_sequences[0], sequences[i])
            if alignments:
                # Get the best alignment
                alignment = alignments[0]
                target, query = alignment.target, alignment.query
                
                # Update aligned sequences
                aligned_sequences = [target, query]
        
        return aligned_sequences
    
    def _align_pairwise_local(self, sequences: List[str]) -> List[str]:
        """Align sequences using BioPython's pairwise local alignment"""
        if len(sequences) < 2:
            return sequences
        
        # Use progressive alignment for multiple sequences
        aligned_sequences = [sequences[0]]
        
        for i in range(1, len(sequences)):
            # Align current sequence with the first aligned sequence
            aligner = Align.PairwiseAligner()
            aligner.mode = 'local'
            aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
            aligner.open_gap_score = -10
            aligner.extend_gap_score = -0.5
            
            alignments = aligner.align(aligned_sequences[0], sequences[i])
            if alignments:
                # Get the best alignment
                alignment = alignments[0]
                target, query = alignment.target, alignment.query
                
                # Update aligned sequences
                aligned_sequences = [target, query]
        
        return aligned_sequences
    
    def _create_alignment_matrix(self, aligned_sequences: List[str]) -> List[List[str]]:
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
        max_length = max(len(seq) for seq in alignment_matrix) if alignment_matrix else 0
        
        for col in range(max_length):
            # Count amino acids at this position
            aa_counts = {}
            for row in range(num_sequences):
                if col < len(alignment_matrix[row]):
                    aa = alignment_matrix[row][col]
                    if aa != '-':  # Skip gaps
                        aa_counts[aa] = aa_counts.get(aa, 0) + 1
            
            if aa_counts:
                # Find most common amino acid
                most_common = max(aa_counts.items(), key=lambda x: x[1])
                consensus.append(most_common[0])
            else:
                # All gaps at this position
                consensus.append('-')
        
        return ''.join(consensus)
