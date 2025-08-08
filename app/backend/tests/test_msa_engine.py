import pytest
import tempfile
import os
import subprocess
from unittest.mock import patch, MagicMock
from Bio import AlignIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

from backend.msa.msa_engine import MSAEngine
from backend.models.models import AlignmentMethod, MSAResult, MSASequence


class TestMSAEngine:
    """Test cases for MSAEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.msa_engine = MSAEngine()
        self.test_sequences = [
            ("seq1", "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"),
            ("seq2", "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"),
            ("seq3", "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS")
        ]
    
    def test_msa_engine_initialization(self):
        """Test MSAEngine initialization"""
        assert self.msa_engine is not None
        assert hasattr(self.msa_engine, 'supported_methods')
        assert len(self.msa_engine.supported_methods) > 0
    
    def test_supported_methods(self):
        """Test that all expected alignment methods are supported"""
        expected_methods = [
            AlignmentMethod.MUSCLE,
            AlignmentMethod.MAFFT,
            AlignmentMethod.CLUSTALO,
            AlignmentMethod.PAIRWISE_GLOBAL,
            AlignmentMethod.PAIRWISE_LOCAL
        ]
        
        for method in expected_methods:
            assert method in self.msa_engine.supported_methods
    
    def test_create_msa_invalid_method(self):
        """Test create_msa with invalid alignment method"""
        with pytest.raises(ValueError, match="Unsupported alignment method"):
            self.msa_engine.create_msa(self.test_sequences, "invalid_method")
    
    def test_create_msa_empty_sequences(self):
        """Test create_msa with empty sequences list"""
        with pytest.raises(ValueError, match="No valid sequences provided"):
            self.msa_engine.create_msa([], AlignmentMethod.MUSCLE)
    
    def test_create_alignment_matrix(self):
        """Test _create_alignment_matrix method"""
        aligned_sequences = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK",
            "ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS"
        ]
        
        matrix = self.msa_engine._create_alignment_matrix(aligned_sequences)
        
        assert len(matrix) == 3
        assert len(matrix[0]) == len(aligned_sequences[0])
        assert matrix[0][0] == 'E'
        assert matrix[1][0] == 'E'
        assert matrix[2][0] == 'E'
    
    def test_create_alignment_matrix_empty(self):
        """Test _create_alignment_matrix with empty sequences"""
        matrix = self.msa_engine._create_alignment_matrix([])
        assert matrix == []
    
    def test_generate_consensus(self):
        """Test _generate_consensus method"""
        alignment_matrix = [
            list("EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"),
            list("EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"),
            list("ELQLQESGPGLVKPSETLSLTCAVSGVSFSDYHWAWIRDPPGKGLEWIGDINHRGHTNYNPSLKSRVTVSIDTSKNQFSLKLSSVTAADTAVYFCARDFPNFIFDFWGQGTLVTVSS")
        ]
        
        consensus = self.msa_engine._generate_consensus(alignment_matrix)
        
        assert len(consensus) == len(alignment_matrix[0])
        assert consensus[0] == 'E'  # All sequences start with E
        assert consensus[1] == 'V'  # All sequences have V at position 1
    
    def test_generate_consensus_with_gaps(self):
        """Test _generate_consensus with gaps in alignment"""
        alignment_matrix = [
            list("EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"),
            list("EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"),
            list("EVQLVESGGGLVQPGGSLRLSCAASGFTFSYAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS")
        ]
        
        consensus = self.msa_engine._generate_consensus(alignment_matrix)
        
        assert len(consensus) == len(alignment_matrix[0])
        assert consensus[0] == 'E'  # All sequences start with E
    
    def test_generate_consensus_empty(self):
        """Test _generate_consensus with empty matrix"""
        consensus = self.msa_engine._generate_consensus([])
        assert consensus == ""
    
    def test_align_muscle_success(self):
        """Test MUSCLE alignment with successful execution"""
        # Test with real MUSCLE since it's available
        sequences = ["EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                   "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"]
        
        result = self.msa_engine._align_muscle(sequences)
        
        assert len(result) == 2
        assert len(result[0]) > 0
        assert len(result[1]) > 0
    
    @patch('subprocess.run')
    def test_align_muscle_failure(self, mock_run):
        """Test MUSCLE alignment with subprocess failure"""
        # Mock failed subprocess run
        mock_run.side_effect = subprocess.CalledProcessError(1, "muscle", stderr="MUSCLE not found")
        
        sequences = ["EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"]
        
        with pytest.raises(RuntimeError, match="MUSCLE alignment failed"):
            self.msa_engine._align_muscle(sequences)
    
    def test_align_pairwise_global_single_sequence(self):
        """Test pairwise global alignment with single sequence"""
        sequences = ["EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"]
        
        result = self.msa_engine._align_pairwise_global(sequences)
        
        assert len(result) == 1
        assert result[0] == sequences[0]
    
    def test_align_pairwise_local_single_sequence(self):
        """Test pairwise local alignment with single sequence"""
        sequences = ["EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS"]
        
        result = self.msa_engine._align_pairwise_local(sequences)
        
        assert len(result) == 1
        assert result[0] == sequences[0]
    
    def test_create_msa_result_structure(self):
        """Test that create_msa returns proper MSAResult structure"""
        # Mock the alignment method to return known sequences
        with patch.object(self.msa_engine, '_align_muscle') as mock_align:
            mock_align.return_value = [
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
                "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
            ]
            
            result = self.msa_engine.create_msa(self.test_sequences[:2], AlignmentMethod.MUSCLE)
            
            assert isinstance(result, MSAResult)
            assert result.msa_id is not None
            assert len(result.sequences) == 2
            assert result.alignment_method == AlignmentMethod.MUSCLE
            assert result.consensus is not None
            assert len(result.alignment_matrix) == 2
            assert result.created_at is not None
            assert result.metadata is not None
            assert result.metadata["num_sequences"] == 2
    
    def test_msa_sequence_structure(self):
        """Test that MSASequence objects are created correctly"""
        # Mock the method in the supported_methods dictionary
        mock_align = MagicMock()
        mock_align.return_value = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK"
        ]
        self.msa_engine.supported_methods[AlignmentMethod.MUSCLE] = mock_align
        
        result = self.msa_engine.create_msa(self.test_sequences[:2], AlignmentMethod.MUSCLE)
        
        for i, msa_seq in enumerate(result.sequences):
            assert isinstance(msa_seq, MSASequence)
            assert msa_seq.name == f"seq{i+1}"
            assert msa_seq.original_sequence == self.test_sequences[i][1]
            # The aligned sequence should match what MUSCLE returned (with gaps)
            assert msa_seq.aligned_sequence == mock_align.return_value[i]
            assert msa_seq.start_position == 0
            assert msa_seq.end_position == len(mock_align.return_value[i])
            assert isinstance(msa_seq.gaps, list)
    
    def test_gap_detection(self):
        """Test that gaps are correctly detected in aligned sequences"""
        # Mock the method in the supported_methods dictionary
        mock_align = MagicMock()
        # Create aligned sequences with gaps
        mock_align.return_value = [
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSYFAMSWVRQAPGKGLEWVATISGGGGNTYYLDRVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCVRQTYGGFGYWGQGTLVTVSS",
            "EVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK---"
        ]
        self.msa_engine.supported_methods[AlignmentMethod.MUSCLE] = mock_align
        
        result = self.msa_engine.create_msa(self.test_sequences[:2], AlignmentMethod.MUSCLE)
        
        # Check that gaps are detected in the second sequence
        assert len(result.sequences[0].gaps) == 0  # No gaps in first sequence
        assert len(result.sequences[1].gaps) > 0   # Gaps in second sequence
        
        # Check that gap positions are correct
        expected_gap_positions = [len(mock_align.return_value[1]) - 3, len(mock_align.return_value[1]) - 2, len(mock_align.return_value[1]) - 1]
        assert result.sequences[1].gaps == expected_gap_positions
